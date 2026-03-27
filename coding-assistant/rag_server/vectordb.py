"""Persistent ChromaDB helpers used by the local RAG server."""

from __future__ import annotations

from typing import Any

from rag_server.config import RAGConfig
from rag_server.embeddings import get_embedding, get_embeddings


def _create_client(config: RAGConfig):
    """Create the persistent Chroma client."""
    try:
        import chromadb
    except ImportError as exc:
        raise ImportError(
            "chromadb is required for the RAG server. "
            "Install it before running ingestion or retrieval."
        ) from exc

    config.ensure_directories()
    return chromadb.PersistentClient(path=str(config.persist_dir))


def create_or_load_db(config: RAGConfig):
    """Create or load the persistent Chroma collection."""
    client = _create_client(config)
    return client.get_or_create_collection(
        name=config.collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(
    collection,
    documents: list[dict],
    force: bool = False,
    batch_size: int = 64,
) -> int:
    """Add documents to Chroma, skipping duplicates unless forced."""
    if force:
        existing_ids = set()
    else:
        existing = collection.get(include=[], limit=collection.count())
        existing_ids = set(existing.get("ids", []))

    new_documents = []
    for document in documents:
        chunk_id = document["metadata"]["chunk_id"]
        if not force and chunk_id in existing_ids:
            continue

        new_documents.append(
            {
                "id": chunk_id,
                "text": document["text"],
                "metadata": {
                    "filename": document["metadata"]["filename"],
                    "chunk_id": chunk_id,
                },
            }
        )

    if not new_documents:
        return 0

    embeddings = get_embeddings([document["text"] for document in new_documents])
    for start in range(0, len(new_documents), batch_size):
        batch_documents = new_documents[start : start + batch_size]
        batch_embeddings = embeddings[start : start + batch_size]
        collection.add(
            ids=[document["id"] for document in batch_documents],
            documents=[document["text"] for document in batch_documents],
            metadatas=[document["metadata"] for document in batch_documents],
            embeddings=batch_embeddings,
        )

    return len(new_documents)


def query(collection, text: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Query the persistent collection by text."""
    query_embedding = get_embedding(text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches: list[dict[str, Any]] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        matches.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": float(distance),
            }
        )

    return matches
