# Definition of Done

Use this checklist before recording the demo or submitting.

## Planning and documentation
- [ ] planning docs committed before major implementation
- [ ] state diagram present
- [ ] sequence diagrams present
- [ ] README includes setup instructions
- [ ] requirements.txt present

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
- [ ] tools dynamically loaded

## RAG server
- [ ] ingestion pipeline works
- [ ] Chroma persists to disk
- [ ] Fusion Retrieval implemented
- [ ] docs retrieval is demonstrably useful

## Demo
- [ ] at least two non-trivial tasks completed
- [ ] all three MCP servers visibly invoked
- [ ] agent actions are visible during demo

## Reflection
- [ ] compare at least two LLMs on same coding task
- [ ] discuss design decisions
- [ ] discuss RAG technique impact
- [ ] describe what would be improved with more time
