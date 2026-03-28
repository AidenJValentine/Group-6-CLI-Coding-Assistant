# Module Spec: Agent Loop

## Goal
Implement the autonomous reasoning loop as a LangGraph state machine. The graph routes user input through either a ReAct debug subgraph or a plan-and-execute build subgraph, then exits through a shared responder node.

## Files
- `src/assistant/agent/loop.py` — LangGraph graph definition and compiled graph
- `src/assistant/agent/state.py` — AgentState TypedDict
- `src/assistant/agent/planner.py` — planner logic called by planner_node
- `src/assistant/agent/message_builder.py` — prompt/message assembly utilities

## Graph topology

```
input_handler
    ├─ slash command ──► handle_slash_command ──► END
    └─ task ──────────► mode_classifier
                            ├─ debug ──► [Debug subgraph]
                            │             agent_node
                            │               ├─ tool_call ──► tool_executor ──► agent_node (loop)
                            │               └─ done ───────────────────────► responder
                            └─ build ──► [Build subgraph]
                                          planner_node
                                            └─ Send() fan-out ──► parallel_executor
                                                                     └─ synthesizer ──► responder
responder ──► END
```

### Node descriptions

| Node | Description |
|---|---|
| `input_handler` | Detects slash commands (lines starting with `/`); routes to `handle_slash_command` or `mode_classifier` |
| `handle_slash_command` | Processes `/mode debug`, `/mode build`, `/help`, `/exit`; updates state and returns to idle |
| `mode_classifier` | Reads `state["execution_mode"]` and routes to the correct subgraph |
| `agent_node` | Debug mode: calls LLM with `agent_model`; conditional edge to `tool_executor` or `responder` |
| `tool_executor` | Executes the tool requested in the last message; appends result to state; loops back to `agent_node` |
| `planner_node` | Build mode: calls `planner.py` with `agent_model`; writes `state["plan"]` |
| `parallel_executor` | Executes one plan step; invoked once per `Send()` fan-out; uses `executor_model` |
| `synthesizer` | Collects `parallel_executor` results; builds final context in plan-list order |
| `responder` | Shared exit node: streams final output to CLI; saves to history |

## State model

`state.py` defines `AgentState` as a `TypedDict`:

```python
class AgentState(TypedDict):
    original_task: str
    messages: list[dict]          # Full conversation history (role/content dicts)
    iteration_count: int
    max_iterations: int
    execution_mode: str           # "debug" | "build"
    tool_history: list[dict]      # Record of every tool call and its result
    plan: list[dict]              # Build mode: steps from planner_node
                                  # Each entry: {"id": str, "step": str, "depends_on": list[str]}
    final_answer: str
    status: str                   # "running" | "completed" | "failed" | "cancelled"
```

## Execution modes

### /mode debug (default on startup)
- Routes through the ReAct subgraph
- Uses `agent_model` (strongest available) for all reasoning
- Max iterations guard: when `iteration_count >= max_iterations`, transition to `responder` with message: `"Max iterations reached. Stopping."`
- Every write-class tool call triggers a confirmation prompt before execution

### /mode build
- Routes through the plan-and-execute subgraph
- `planner_node` calls `planner.py` to produce a `plan: list[dict]`
- `Send()` fans out all steps to `parallel_executor` (MVP: all steps independent, all fan out immediately)
- Each `parallel_executor` step uses `executor_model` (cheaper/faster model)
- `synthesizer` collects results in plan-list order
- Write-class tools: prompt once per tool type per batch; auto-approve the rest of that type in the batch

### Mode persistence
Mode is stored in `AgentState.execution_mode` and persists across turns until the user issues a new `/mode` command.

## Slash commands (handled by input_handler / handle_slash_command)

| Command | Effect |
|---|---|
| `/mode debug` | Set `execution_mode = "debug"`, confirm to user |
| `/mode build` | Set `execution_mode = "build"`, confirm to user |
| `/help` | Print available commands |
| `/exit` | Quit REPL |

## Planner (planner.py)

`planner_node` delegates to `planner.py`. The planner prompt instructs the LLM to output a structured step list:

```json
[
  {"id": "1", "step": "Read the existing tests", "depends_on": []},
  {"id": "2", "step": "Write new utility function", "depends_on": []},
  {"id": "3", "step": "Add tests for the new function", "depends_on": []}
]
```

**MVP:** `depends_on` is always `[]`; all steps fan out immediately.
**Post-MVP:** Planner emits real dependency edges; `parallel_executor` waits for blocked steps; `synthesizer` respects ordering.

## Required behaviors
- Gracefully handle denied tool execution: append a denial observation to messages and continue the graph
- Stream text tokens to CLI from the `responder` node
- Maintain separation between reasoning state and UI

## Stop conditions
- Model signals completion → `responder`
- `iteration_count >= max_iterations` → `responder` with user-facing message (debug mode)
- Unrecoverable provider or tool error → set `status = "failed"`, transition to `responder`

## Minimum system prompt expectations
The system prompt should tell the model:
- it is an autonomous coding assistant
- it may use available tools when needed
- it should only finish when the task is complete or it is blocked
- it should explain what it accomplished at the end

## Done criteria
- `StateGraph.compile()` runs without error
- Debug subgraph: mock provider + mock tool → loop resolves and reaches `responder`
- Build subgraph: planner produces plan → `Send()` fan-out → synthesizer collects all results
- Max-iteration guard tested (debug mode): hitting limit produces user-facing message

## Post-MVP / Not implemented
- Dependency-aware step scheduling in build mode (real `depends_on` edges in planner output; executor fans out only unblocked steps; synthesizer respects ordering)
- Automatic mode detection via keyword/LLM classifier
- Mid-task mode switching (reasoning spiral detection)
- Token usage tracking and display
- Undo/rollback file edits
