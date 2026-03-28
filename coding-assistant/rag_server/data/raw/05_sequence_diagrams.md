# Sequence Diagrams

## Scenario 1: Ask documentation question through RAG MCP server

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Agent as Agent Loop
    participant Provider as LLM Provider
    participant MCP as MCP Client
    participant RAG as Custom RAG MCP Server

    User->>CLI: Ask about a library feature
    CLI->>Agent: submit task
    Agent->>Provider: request next action + tool schema
    Provider-->>Agent: tool call: docs_search(query)
    Agent->>MCP: invoke docs_search
    MCP->>RAG: query documentation index
    RAG-->>MCP: top retrieved chunks
    MCP-->>Agent: normalized tool result
    Agent->>Provider: continue with retrieval result
    Provider-->>Agent: final answer
    Agent-->>CLI: stream final response
    CLI-->>User: show answer + tool usage
```

## Scenario 2: Read file and make edit with confirmation mode

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Agent as Agent Loop
    participant Provider as LLM Provider
    participant MCP as MCP Client
    participant FS as Filesystem MCP Server

    User->>CLI: "Read file X and fix bug"
    CLI->>Agent: submit task
    Agent->>Provider: request next action
    Provider-->>Agent: tool call: read_file(X)
    Agent->>MCP: invoke read_file
    MCP->>FS: read file
    FS-->>MCP: file contents
    MCP-->>Agent: file contents
    Agent->>Provider: continue with file content
    Provider-->>Agent: tool call: write_file(X, patch)
    Agent-->>CLI: request user confirmation
    User-->>CLI: approve
    CLI-->>Agent: approval granted
    Agent->>MCP: invoke write_file
    MCP->>FS: write file
    FS-->>MCP: success
    MCP-->>Agent: success result
    Agent->>Provider: continue after edit
    Provider-->>Agent: final completion message
    Agent-->>CLI: stream result
    CLI-->>User: show edit complete
```

## Scenario 3: Search web and create implementation plan

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Agent as Agent Loop
    participant Provider as LLM Provider
    participant MCP as MCP Client
    participant EXT as External MCP Server

    User->>CLI: "Search web for topic and plan implementation"
    CLI->>Agent: submit task
    Agent->>Provider: request next action
    Provider-->>Agent: tool call: web_search(query)
    Agent->>MCP: invoke web_search
    MCP->>EXT: search external resource
    EXT-->>MCP: search results
    MCP-->>Agent: normalized result list
    Agent->>Provider: continue with search findings
    Provider-->>Agent: implementation plan
    Agent-->>CLI: stream plan
    CLI-->>User: show tool call + answer
```
