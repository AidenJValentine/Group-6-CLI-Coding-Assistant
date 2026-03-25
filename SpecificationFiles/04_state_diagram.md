# State Diagram

This diagram reflects the LangGraph node topology. Use it in markdown-capable viewers or convert to an image for the repo/demo.

```mermaid
flowchart TD
    A([User Input]) --> B[input_handler]
    B -->|slash command| C[handle_slash_command]
    B -->|task| D[mode_classifier]
    C --> Z([Idle — await next input])

    D -->|execution_mode = debug| E["agent_node\nuses agent_model"]
    D -->|execution_mode = build| F["planner_node\nuses agent_model"]

    E -->|tool call| G{tool class?}
    G -->|read class| I[tool_executor]
    G -->|write class| H[await user approval]
    H -->|approved| I
    H -->|denied| E
    I --> E
    E -->|done or max_iterations hit| R[responder]

    F --> J["Send() fan-out\nparallel_executor\nuses executor_model"]
    J --> K[synthesizer]
    K --> R

    R --> Z
```

## Node explanations

| Node | Role |
|---|---|
| `input_handler` | Entry point. Detects `/` slash commands and routes them out early; otherwise passes to `mode_classifier` |
| `handle_slash_command` | Handles `/mode debug`, `/mode build`, `/help`, `/exit`; confirms switch to user |
| `mode_classifier` | Reads `AgentState.execution_mode`; routes to debug or build subgraph |
| `agent_node` | ReAct agent step (debug mode). Calls LLM, decides tool call or final answer |
| `tool_executor` | Runs the MCP tool requested by `agent_node`; appends result to state |
| `await user approval` | Write-class tool in debug mode: blocks until user approves or denies |
| `planner_node` | Build mode entry. Calls `planner.py` to produce `state["plan"]` |
| `parallel_executor` | Executes one plan step (invoked N times via `Send()` fan-out) |
| `synthesizer` | Collects all `parallel_executor` results; assembles final context |
| `responder` | Shared exit node. Streams final answer to CLI; saves to history |

## Confirmation rules (tool_executor path)

| Tool class | debug mode | build mode |
|---|---|---|
| read | auto-execute | auto-execute |
| write | prompt every call | prompt once per type per batch |
