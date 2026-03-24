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

## Approval controller requirements
Support two modes:
- `confirm`: ask user before execution
- `auto`: execute immediately

For confirm mode, return an approval request object to the CLI before execution.

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
