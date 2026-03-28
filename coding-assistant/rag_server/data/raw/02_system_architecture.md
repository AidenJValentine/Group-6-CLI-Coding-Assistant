# System Architecture

## Top-level design

The system is divided into six major components:

1. **CLI Interface**
2. **Agent Loop**
3. **Provider Layer**
4. **MCP Client**
5. **Execution/Approval Controller**
6. **Custom RAG MCP Server**

## Architectural goals
- modularity
- model-agnostic design
- transparent tool usage
- simple local development
- clean demonstration path

## Component responsibilities

### 1. CLI Interface
Responsibilities:
- start REPL session
- read user commands
- display streaming assistant text
- display tool-call events
- show approval prompts when confirmation mode is enabled
- show final outcome and errors clearly

The CLI should not contain agent reasoning logic.

### 2. Agent Loop
Responsibilities:
- maintain task state
- build prompts for the selected provider
- ask model what to do next
- parse tool requests
- execute tools through execution controller/MCP client
- feed observations back to the model
- stop on completion or failure threshold

### 3. Provider Layer
Responsibilities:
- expose one common interface for different models
- support Ollama and one cloud model
- normalize request/response formats
- support streaming text
- support tool-capable model interactions

### 4. MCP Client
Responsibilities:
- connect to multiple MCP servers
- dynamically discover available tools
- expose unified tool registry to the agent loop
- call tools and return normalized results

### 5. Execution/Approval Controller
Responsibilities:
- decide whether a tool call needs user confirmation
- support two modes:
  - confirm-before-execution
  - auto-execute
- log command/tool execution metadata
- provide safe formatting of results back to agent loop

### 6. Custom RAG MCP Server
Responsibilities:
- ingest documentation once
- build and persist vector store
- answer documentation search queries
- apply Fusion Retrieval
- expose retrieval as an MCP tool

## Recommended runtime flow

1. User enters task in CLI
2. CLI passes task to agent loop
3. Agent loop requests next action from provider
4. If provider returns tool call:
   - resolve tool through MCP client
   - execute through approval controller
   - pass result back into loop
5. Repeat until model returns completion/final answer
6. CLI prints final response

## Data flow summary

- User task flows from CLI to agent loop
- Agent loop sends model messages through provider layer
- Provider returns text and/or tool calls
- Tool calls flow to MCP client and execution controller
- Results flow back into agent loop
- Final result flows to CLI

## Recommended technology choices

### Language
- Python

### Libraries
- Typer or Click for CLI
- Rich for styled terminal output and streaming display
- **LangGraph** for agent loop state machine (required)
- **LiteLLM** for provider abstraction (required — replaces hand-rolled provider classes)
- official MCP Python SDK
- ChromaDB for vector storage
- sentence-transformers for embeddings

### Providers
- Ollama: local model option
- OpenAI or Anthropic: cloud option

## Failure handling
- max iteration count to prevent loops
- clear error surface in terminal
- graceful fallback if a server is unavailable
- distinguish model failure vs tool failure vs user denial
