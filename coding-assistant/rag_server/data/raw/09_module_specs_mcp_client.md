# Module Spec: MCP Client and Tool Registry

## Goal
Connect to multiple MCP servers, dynamically load tools, and expose a unified invocation interface.

## Files
- `src/assistant/mcp/client.py`
- `src/assistant/mcp/server_config.py`
- `src/assistant/mcp/adapters.py`
- `src/assistant/tools/registry.py`
- `src/assistant/tools/executor.py`
- `src/assistant/tools/approval.py`

## Functional requirements
1. Connect to configured MCP servers on startup
2. Discover available tools from each server
3. Register tools in a unified local registry
4. Expose:
   - list_tools()
   - invoke_tool(name, arguments)
5. Route tool calls to the correct server
6. Normalize returned results

## Required server coverage
- filesystem MCP server
- one external resource MCP server
- custom RAG MCP server

## Tool classification

Tools are classified into two classes. This dict lives in `approval.py`:

```python
TOOL_CLASSES = {
    "read":  ["read_file", "list_directory", "search_docs", "web_search"],
    "write": ["write_file", "edit_file", "run_command", "delete_file"],
}
```

## Mode-aware confirmation rules

| Tool class | debug mode | build mode |
|---|---|---|
| `read` | auto-execute (no prompt) | auto-execute (no prompt) |
| `write` | prompt before **every** call | prompt once per tool type per batch; auto-approve remaining calls of that same type in the batch |

The old binary `confirm` / `auto` execution mode is replaced by this 3-way rule (tool class × agent mode). The approval controller receives the current `execution_mode` from `AgentState` to apply the correct rule.

For write-class tools in confirm scenarios, return an approval request object to the CLI before execution.

## Recommended normalized tool metadata
- `name`
- `description`
- `input_schema`
- `server_name`

## Error handling
- unknown tool
- server offline
- malformed arguments
- execution failure

## Done criteria
- tools from all required servers appear in one registry
- at least one real tool from each server can be invoked
- CLI can show which server/tool was used
