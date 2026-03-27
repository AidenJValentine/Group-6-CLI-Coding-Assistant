"""CLI application loop for reading input and printing responses."""

from assistant.agent.loop import run_agent
from assistant.cli.prompts import prompt_for_approval
from assistant.cli.renderer import (
    render_assistant_text,
    render_banner,
    render_error,
    render_status,
    render_tool_events,
)
from assistant.config import RuntimeConfig


def run_cli(config: RuntimeConfig) -> None:
    """Run the Milestone 2 assistant REPL."""
    session_state = {"execution_mode": config.execution_mode}
    render_banner(config)

    while True:
        try:
            user_input = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        normalized_input = user_input.strip()
        if normalized_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not normalized_input:
            continue

        try:
            result = run_agent(
                normalized_input,
                session_state,
                max_iterations=config.max_iterations,
                approval_mode=config.approval_mode,
                approval_handler=prompt_for_approval,
            )
        except Exception as exc:  # pragma: no cover - defensive CLI guard
            render_error(str(exc))
            continue

        session_state["execution_mode"] = result.get("execution_mode", "debug")
        render_tool_events(result.get("latest_events", []))
        render_assistant_text(result.get("final_answer", ""))
        render_status(result.get("status", "unknown"))

        if result.get("exit_requested"):
            break
