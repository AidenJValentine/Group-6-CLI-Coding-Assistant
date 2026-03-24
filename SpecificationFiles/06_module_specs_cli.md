# Module Spec: CLI Interface

## Goal
Implement a terminal REPL that accepts user tasks, streams assistant output, shows tool calls clearly, and supports approval prompts.

## Files
- `src/assistant/cli/app.py`
- `src/assistant/cli/renderer.py`
- `src/assistant/cli/prompts.py`
- `src/assistant/main.py`

## Functional requirements
1. Start a REPL loop from command line
2. Accept configuration flags:
   - provider
   - model
   - execution mode (`confirm` or `auto`)
3. Print a clear banner with assistant name
4. Accept user prompt
5. Pass prompt to agent loop
6. Render streamed assistant tokens
7. Render tool-call events in a visually distinct format
8. Prompt user for approval when required
9. Show final status: success, failure, cancelled

## Suggested interface
```bash
python -m assistant.main --provider ollama --model llama3 --mode confirm
```

## Input/output contract

### Input to CLI
- user task string
- runtime config

### Output from CLI
- rendered text stream
- rendered tool events
- approval responses
- final summary

## Rendering requirements
- use Rich if possible
- tool call block should show:
  - tool name
  - arguments summary
  - execution status
- errors should be visibly separated
- approval prompt should explicitly say approve/deny

## Non-functional requirements
- do not embed model logic here
- do not directly call MCP servers here
- thin orchestration only

## Done criteria
- user can launch REPL
- submit task
- see streamed model output
- see at least one mocked or real tool call displayed
- approve or deny a tool action
