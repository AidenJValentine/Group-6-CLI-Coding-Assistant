# Module Spec: Custom RAG MCP Server

## Goal
Implement a local MCP server that indexes library documentation once, persists the vector DB, and answers documentation queries using Fusion Retrieval.

## Files
- `rag_server/server.py`
- `rag_server/ingest.py`
- `rag_server/retrieval.py`
- `rag_server/chunking.py`
- `rag_server/embeddings.py`
- `rag_server/vectordb.py`
- `rag_server/config.py`

## Functional requirements

### A. Ingestion pipeline
1. Load documentation files from a configured source directory
2. Split content into chunks
3. Generate embeddings
4. Store chunks + metadata in ChromaDB
5. Persist DB to disk
6. Skip reindex if DB already exists unless force-rebuild is requested

### B. Retrieval pipeline
1. Accept a user query
2. Generate 3 to 5 query rewrites
3. Retrieve top-k chunks per rewritten query
4. Deduplicate results
5. Merge/rerank by frequency + similarity score
6. Return top final chunks

### C. MCP exposure
Expose at least one MCP tool such as:
- `docs_search(query: str, top_k: int = 5)`

## Suggested documentation corpus
Pick one library that is relevant to the project, such as:
- LangChain
- ChromaDB
- MCP Python SDK

## Metadata per chunk
- source file
- section heading if available
- chunk id
- character range or chunk index

## Chunking recommendation
Start with simple heading-aware chunking.
If time allows, improve with semantic chunking.

## Persistence requirement
The index build should be one-time setup. Future sessions should reuse the persisted Chroma database.

## Done criteria
- can ingest docs from disk
- Chroma persists locally
- repeated runs do not rebuild unless requested
- MCP tool returns relevant chunks
- retrieval path uses Fusion Retrieval, not just one raw query
