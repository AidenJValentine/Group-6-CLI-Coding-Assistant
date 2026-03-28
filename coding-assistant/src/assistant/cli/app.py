"""CLI application loop for reading input and printing responses."""

from assistant.agent.loop import run_agent
from assistant.cli.renderer import render_banner, render_error, render_result
from assistant.config import RuntimeConfig


def run_cli(config: RuntimeConfig) -> None:
    """Run the assistant REPL."""
    render_banner(config)

    while True:
        try:
            prompt = f"[{config.execution_mode}] > "
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        normalized_input = user_input.strip()
        if not normalized_input:
            continue
        if normalized_input.lower() in {"/exit", "/quit", "exit", "quit"}:
            print("Goodbye!")
            break

        try:
            result = run_agent(normalized_input, config)
        except Exception as exc:  # pragma: no cover - defensive CLI guard
            render_error(str(exc))
            continue

        render_result(result)

        if result.get("exit_requested"):
            break

        # Sync mode if changed by /mode slash command
        new_mode = result.get("execution_mode", config.execution_mode)
        if new_mode != config.execution_mode:
            config.execution_mode = new_mode
