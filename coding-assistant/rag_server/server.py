from mcp.server.fastmcp import FastMCP
from rag_server.ingest import build_index
from rag_server.retrieval import retrieve_documents

mcp = FastMCP("rag-server")

@mcp.tool()
def search_docs(query: str, top_k: int = 5) -> dict:
    build_index(force_rebuild=False)

    retrieval_result = retrieve_documents(query, top_k=top_k)

    results = []
    for item in retrieval_result["results"]:
        metadata = item.get("metadata", {})
        results.append({
            "text": item.get("text", ""),
            "source": metadata.get("filename") or metadata.get("source_file", ""),
            "chunk_id": metadata.get("chunk_id", ""),
        })

    return {
        "query": retrieval_result["query"],
        "results": results,
    }

if __name__ == "__main__":
    mcp.run()