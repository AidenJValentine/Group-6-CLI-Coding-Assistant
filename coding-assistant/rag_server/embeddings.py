"""Sentence-transformer embedding helpers for the RAG server."""

from __future__ import annotations

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_MODEL = None


def _load_model():
    """Load the embedding model lazily for local reuse."""
    global _MODEL

    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for the RAG server. "
                "Install it before running ingestion or retrieval."
            ) from exc

        _MODEL = SentenceTransformer(MODEL_NAME)

    return _MODEL


def get_embedding(text: str) -> list[float]:
    """Return an embedding for one text string."""
    model = _load_model()
    embedding = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return embedding[0].tolist()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Return embeddings for multiple text strings."""
    if not texts:
        return []

    model = _load_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.tolist()
