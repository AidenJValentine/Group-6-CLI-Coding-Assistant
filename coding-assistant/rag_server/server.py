"""Callable server interface for the local documentation retriever."""

from __future__ import annotations

from rag_server.ingest import build_index
from rag_server.retrieval import retrieve_documents


def docs_search(query: str, top_k: int = 5) -> dict:
    """Return structured documentation search results for one query."""
    build_index(force_rebuild=False)
    retrieval_result = retrieve_documents(query, top_k=top_k)

    results = []
    for item in retrieval_result["results"]:
        metadata = item.get("metadata", {})
        results.append(
            {
                "text": item.get("text", ""),
                "source": metadata.get("filename") or metadata.get("source_file", ""),
                "chunk_id": metadata.get("chunk_id", ""),
            }
        )

    return {
        "query": retrieval_result["query"],
        "results": results,
    }


def _print_demo_results(search_result: dict) -> None:
    """Print a readable demo view of retrieval results."""
    print("RAG Server Demo")
    print(f"Query: {search_result['query']}")
    print()

    if not search_result["results"]:
        print("No results found.")
        return

    for index, result in enumerate(search_result["results"], start=1):
        print(f"Result {index}")
        print(f"Source: {result['source']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print("Text:")
        print(result["text"])
        print()


if __name__ == "__main__":
    index_result = build_index(force_rebuild=False)
    print("Index Status")
    print(index_result)
    print()

    demo_query = "How does the system architecture describe the RAG server?"
    demo_result = docs_search(demo_query, top_k=3)
    _print_demo_results(demo_result)
