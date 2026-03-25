"""Fusion retrieval for documentation search over the local vector store."""

from __future__ import annotations

import re

from rag_server.config import get_config
from rag_server.ingest import build_index
from rag_server.vectordb import create_or_load_db, query


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "with",
}


def generate_query_rewrites(query: str, max_queries: int = 4) -> list[str]:
    """Generate a small set of deterministic query rewrites."""
    cleaned = " ".join(query.split())
    keywords = " ".join(
        word for word in re.findall(r"[A-Za-z0-9_]+", cleaned.lower()) if word not in STOPWORDS
    )

    candidates = [
        cleaned,
        f"{cleaned} documentation",
        f"{cleaned} example usage",
        keywords or cleaned,
        f"{cleaned} reference guide",
    ]

    rewrites: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = candidate.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        rewrites.append(normalized)
        seen.add(key)
        if len(rewrites) >= max_queries:
            break

    return rewrites


def _fuse_results(result_sets: list[list[dict]], top_k: int) -> list[dict]:
    """Merge retrieval results using simple frequency and similarity scoring."""
    merged: dict[str, dict] = {}

    for result_set in result_sets:
        for rank, item in enumerate(result_set):
            metadata = item.get("metadata", {})
            chunk_id = metadata.get("chunk_id", "")
            if not chunk_id:
                continue

            entry = merged.setdefault(
                chunk_id,
                {
                    "text": item["text"],
                    "metadata": metadata,
                    "frequency": 0,
                    "best_similarity": 0.0,
                    "similarity_total": 0.0,
                    "rank_bonus": 0.0,
                    "score": 0.0,
                },
            )

            distance = float(item.get("distance", 0.0))
            similarity = 1.0 / (1.0 + distance)
            entry["frequency"] += 1
            entry["best_similarity"] = max(entry["best_similarity"], similarity)
            entry["similarity_total"] += similarity
            entry["rank_bonus"] += 1.0 / (rank + 1)

    ranked = []
    for item in merged.values():
        average_similarity = item["similarity_total"] / item["frequency"]

        # Keep the ranking simple and explicit:
        # frequency rewards chunks returned by multiple rewritten queries,
        # similarity rewards chunks that are semantically close to those queries.
        item["score"] = (
            item["frequency"] * 2.0
            + average_similarity
            + item["best_similarity"]
            + (item["rank_bonus"] * 0.1)
        )
        item["average_similarity"] = average_similarity
        ranked.append(item)

    ranked.sort(
        key=lambda item: (item["score"], item["frequency"], item["best_similarity"]),
        reverse=True,
    )
    return ranked[:top_k]


def retrieve_documents(query_text: str, top_k: int = 5) -> dict:
    """Retrieve documentation chunks using multi-query fusion retrieval."""
    config = get_config()
    build_index(force_rebuild=False)
    collection = create_or_load_db(config)

    rewrites = generate_query_rewrites(query_text, max_queries=config.fusion_query_count)
    result_sets: list[list[dict]] = []

    for rewrite in rewrites:
        result_sets.append(query(collection, rewrite, top_k=config.per_query_top_k))

    fused_results = _fuse_results(result_sets, top_k=top_k)
    return {
        "query": query_text,
        "rewrites": rewrites,
        "results": fused_results,
    }
