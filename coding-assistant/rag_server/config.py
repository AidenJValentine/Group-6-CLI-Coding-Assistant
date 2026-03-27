"""Configuration values for embeddings and persistent Chroma storage."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _default_docs_dir(base_dir: Path) -> Path:
    """Pick a reasonable local docs directory for ingestion."""
    configured = os.getenv("RAG_DOCS_DIR")
    if configured:
        return Path(configured).expanduser().resolve()

    raw_dir = base_dir / "data" / "raw"
    if any(raw_dir.glob("**/*")):
        return raw_dir

    # Fall back to the repository specification docs for local development.
    return base_dir.parent / "SpecificationFiles"


@dataclass(slots=True)
class RAGConfig:
    """Runtime settings for the local RAG server."""

    base_dir: Path
    docs_dir: Path
    persist_dir: Path
    collection_name: str = "assistant_docs"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 900
    chunk_overlap: int = 150
    per_query_top_k: int = 6
    fusion_query_count: int = 4
    default_top_k: int = 5
    batch_size: int = 64
    allowed_suffixes: tuple[str, ...] = (".md", ".mdx", ".txt", ".rst")

    def ensure_directories(self) -> None:
        """Create any directories needed for persistence."""
        self.persist_dir.mkdir(parents=True, exist_ok=True)


def get_config() -> RAGConfig:
    """Build the default RAG configuration for this repository."""
    base_dir = Path(__file__).resolve().parent
    docs_dir = _default_docs_dir(base_dir)
    persist_dir = Path(os.getenv("RAG_PERSIST_DIR", base_dir / "data" / "chroma"))

    config = RAGConfig(
        base_dir=base_dir,
        docs_dir=docs_dir,
        persist_dir=persist_dir,
        collection_name=os.getenv("RAG_COLLECTION_NAME", "assistant_docs"),
        embedding_model_name=os.getenv(
            "RAG_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        ),
    )
    config.ensure_directories()
    return config
