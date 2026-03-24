# Module Spec: Agent Loop

## Goal
Implement the autonomous reasoning loop that iteratively queries the model, executes tools, appends observations, and stops when the task is done.

## Files
- `src/assistant/agent/loop.py`
- `src/assistant/agent/state.py`
- `src/assistant/agent/planner.py`
- `src/assistant/agent/message_builder.py`

## Functional requirements
1. Accept initial user task and runtime config
2. Build message history including:
   - system prompt
   - tool descriptions
   - prior observations
3. Call selected provider for next action
4. Distinguish between:
   - text-only response
   - tool call response
   - final completion response
5. Execute tool call through tool executor / MCP client
6. Append tool result to state
7. Repeat until:
   - final answer
   - max iterations reached
   - fatal error

## State model
Recommended fields:
- `original_task`
- `messages`
- `iteration_count`
- `max_iterations`
- `execution_mode`
- `tool_history`
- `final_answer`
- `status`

## Required behaviors
- support at least one tool call per iteration
- gracefully handle denied tool execution by appending a denial observation
- support streamed text forwarding to CLI
- maintain separation between reasoning state and UI

## Stop conditions
- model explicitly signals completion
- `iteration_count >= max_iterations`
- unrecoverable provider/tool error

## Minimum system prompt expectations
The system prompt should tell the model:
- it is an autonomous coding assistant
- it may use available tools when needed
- it should only finish when task is complete or blocked
- it should explain what it accomplished at the end

## Done criteria
- loop can run against mocked provider + mocked tool registry
- successful path tested
- tool-use path tested
- max-iteration safety tested
