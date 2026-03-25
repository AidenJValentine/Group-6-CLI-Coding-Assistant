# Definition of Done

Use this checklist before recording the demo or submitting.

## Planning and documentation
- [x] planning docs committed before major implementation
- [x] state diagram present
- [x] sequence diagrams present
- [ ] README includes setup instructions
- [x] requirements.txt present

## Core architecture
- [ ] agent loop iterates autonomously
- [ ] provider abstraction supports Ollama and one cloud provider
- [ ] modular separation is clear

## CLI and tool visibility
- [ ] REPL works
- [ ] tool calls are visibly displayed
- [ ] responses stream or appear incrementally
- [ ] confirm mode works
- [ ] auto-execute mode works

## MCP integration
- [ ] filesystem server connected
- [ ] external server connected
- [ ] custom RAG server connected
- [x] custom RAG server exposes an MCP-compatible callable interface
- [ ] tools dynamically loaded

## RAG server
- [x] ingestion pipeline loads documentation from disk and chunks it correctly
- [x] chunk metadata includes filename and chunk index or chunk id
- [x] embeddings are generated with sentence-transformers
- [x] Chroma persists to disk
- [x] repeated runs reuse the persisted Chroma database unless force rebuild is requested
- [x] Fusion Retrieval implemented
- [x] Fusion Retrieval uses multi-query retrieval plus merge/deduplication
- [x] retrieved results are relevant and ranked by simple frequency + similarity scoring
- [x] docs_search works as a callable tool interface
- [ ] docs retrieval is demonstrably useful
- [x] RAG server can be demonstrated independently from the main agent loop

## Demo
- [ ] at least two non-trivial tasks completed
- [ ] all three MCP servers visibly invoked
- [ ] agent actions are visible during demo
- [ ] RAG subsystem demo shows index build or reuse plus a successful docs query

## Reflection
- [ ] compare at least two LLMs on same coding task
- [ ] discuss design decisions
- [ ] discuss RAG technique impact
- [ ] describe what would be improved with more time
