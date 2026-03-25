"""Simple overlapping text chunking for documentation files."""

from __future__ import annotations

from pathlib import Path


def _find_chunk_end(text: str, start: int, chunk_size: int) -> int:
    """Choose an end position that avoids cutting mid-word when possible."""
    preferred_end = min(start + chunk_size, len(text))
    if preferred_end >= len(text):
        return len(text)

    window = text[start:preferred_end]
    split_at = max(window.rfind(" "), window.rfind("\n"), window.rfind("\t"))

    if split_at > 0:
        return start + split_at

    return preferred_end


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks without cutting mid-word when possible."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be 0 or greater")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    text_length = len(cleaned)

    while start < text_length:
        end = _find_chunk_end(cleaned, start, chunk_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - overlap, start + 1)
        while start < text_length and cleaned[start].isspace():
            start += 1

    return chunks


def chunk_document(
    source_path: Path,
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[dict]:
    """Wrap plain text chunks with simple metadata for ingestion."""
    chunks: list[dict] = []
    for chunk_index, chunk in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)):
        chunk_id = f"{source_path.as_posix()}::chunk-{chunk_index}"
        chunks.append(
            {
                "id": chunk_id,
                "text": chunk,
                "metadata": {
                    "source_file": source_path.as_posix(),
                    "filename": source_path.name,
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_index,
                },
            }
        )

    return chunks
