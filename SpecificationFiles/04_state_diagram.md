# State Diagram

Use this Mermaid state diagram directly in markdown-capable viewers or convert it to an image for the repo/demo.

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> AcceptingTask : user enters prompt
    AcceptingTask --> BuildingContext : task accepted

    BuildingContext --> QueryingModel : prompt assembled

    QueryingModel --> DisplayingText : model streams text
    DisplayingText --> QueryingModel : continue stream

    QueryingModel --> ToolDecision : model requests tool
    QueryingModel --> Completed : model returns final answer
    QueryingModel --> Failed : provider error

    ToolDecision --> AwaitingApproval : confirmation mode enabled
    ToolDecision --> ExecutingTool : auto-execute mode enabled

    AwaitingApproval --> ExecutingTool : user approves
    AwaitingApproval --> QueryingModel : user denies / denial observation added

    ExecutingTool --> ObservingResult : tool returns result
    ExecutingTool --> Failed : execution error

    ObservingResult --> BuildingContext : append tool result to conversation

    Completed --> Idle : next user task
    Failed --> Idle : recover / next user task
```

## State explanations

- **Idle**: system waiting for input
- **AcceptingTask**: task capture and initial validation
- **BuildingContext**: prepare system prompt, tool list, conversation state
- **QueryingModel**: ask model for next action
- **DisplayingText**: show streamed assistant tokens
- **ToolDecision**: model has selected a tool call
- **AwaitingApproval**: optional user confirmation step
- **ExecutingTool**: MCP tool or shell-like action is running
- **ObservingResult**: output is normalized and appended to state
- **Completed**: task finished
- **Failed**: unrecoverable error or max-iteration stop
