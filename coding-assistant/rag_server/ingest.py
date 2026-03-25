"""Ingestion pipeline for building the persistent local RAG index."""

from __future__ import annotations

from pathlib import Path

from rag_server.chunking import chunk_document
from rag_server.config import get_config
from rag_server.vectordb import add_documents, create_or_load_db


def _get_raw_docs_dir() -> Path:
    """Return the fixed raw document directory for ingestion."""
    return Path(__file__).resolve().parent / "data" / "raw"


def _iter_source_files(raw_docs_dir: Path) -> list[Path]:
    """Collect supported documentation files from the raw data directory."""
    if not raw_docs_dir.exists():
        raise FileNotFoundError(f"Documentation directory does not exist: {raw_docs_dir}")

    return sorted(
        path
        for path in raw_docs_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}
    )


def build_index(force_rebuild: bool = False) -> dict:
    """Build the persistent vector index from files in ``rag_server/data/raw``."""
    config = get_config()
    raw_docs_dir = _get_raw_docs_dir()
    collection = create_or_load_db(config)

    if collection.count() > 0 and not force_rebuild:
        return {
            "status": "reused",
            "docs_dir": str(raw_docs_dir),
            "persist_dir": str(config.persist_dir),
            "chunk_count": collection.count(),
        }

    if force_rebuild:
        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "chromadb is required for the RAG server. "
                "Install it before running ingestion or retrieval."
            ) from exc

        client = chromadb.PersistentClient(path=str(config.persist_dir))
        try:
            client.delete_collection(config.collection_name)
        except Exception:
            pass
        collection = client.get_or_create_collection(
            name=config.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    source_files = _iter_source_files(raw_docs_dir)
    if not source_files:
        raise ValueError(f"No documentation files found in {raw_docs_dir}")

    all_chunks: list[dict] = []
    for file_path in source_files:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        relative_path = file_path.relative_to(raw_docs_dir)
        file_chunks = chunk_document(
            source_path=relative_path,
            text=text,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        for chunk in file_chunks:
            chunk["metadata"]["filename"] = file_path.name
        all_chunks.extend(file_chunks)

    if not all_chunks:
        raise ValueError(f"No chunks were produced from {raw_docs_dir}")

    stored_count = add_documents(
        collection,
        all_chunks,
        force=force_rebuild,
        batch_size=config.batch_size,
    )

    return {
        "status": "built",
        "docs_dir": str(raw_docs_dir),
        "persist_dir": str(config.persist_dir),
        "file_count": len(source_files),
        "chunk_count": stored_count,
    }


if __name__ == "__main__":
    result = build_index()
    print(result)
