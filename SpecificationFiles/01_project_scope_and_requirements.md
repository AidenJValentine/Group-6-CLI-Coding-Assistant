# Project Scope and Requirements

## Project summary

Build a command-line AI coding assistant that accepts natural-language developer instructions, reasons over a local codebase, invokes tools through MCP servers, edits and executes code, and iterates until the task is complete.

The system is an autonomous agent rather than a plain chatbot. It must visibly show tool usage in the terminal and support both user-confirmed execution and auto-execute mode.

## Required capabilities

### Core
- Agentic loop that continues until completion
- CLI REPL with streamed responses and status indicators
- Tool calling through MCP
- Provider abstraction supporting:
  - Ollama
  - at least one cloud provider
- Dynamically loaded MCP tools

### Required MCP servers
1. Filesystem server
2. At least one external resource server
3. Custom local RAG MCP server over library documentation

### Custom RAG server requirements
- One-time ingestion/index build
- Persistent vector database reused across sessions
- File loading
- Chunking
- Embedding
- Vector storage
- Query endpoint
- At least one advanced RAG technique

## Recommended advanced RAG choice

Use **Fusion Retrieval** as the advanced RAG technique because it is:
- understandable
- feasible for a class project
- easy to explain in reflection/demo
- meaningfully stronger than a naive single-query retriever

### Fusion Retrieval approach
1. Receive original user question
2. Generate 3 to 5 reformulated search queries
3. Retrieve top-k chunks for each
4. Merge and rerank deduplicated results
5. Return top final contexts

Optional addition: use semantic chunking if time allows.

## Non-goals for first implementation
- full IDE extension
- multi-user system
- advanced permissions engine
- image input
- rollback/undo stack
- conversation persistence across every tool state

## Deliverables implied by planning
- repo with clear commit history showing planning before coding
- planning docs and diagrams committed
- working system demo
- reflection comparing at least two models on the same task
