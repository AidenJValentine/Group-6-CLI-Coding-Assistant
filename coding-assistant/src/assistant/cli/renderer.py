"""Rendering helpers for terminal output."""

from collections.abc import Iterable

from assistant.config import RuntimeConfig


def render_banner(config: RuntimeConfig) -> None:
    """Print a simple startup banner."""
    print("AI Coding Assistant")
    print(
        f"mode={config.execution_mode} | provider={config.provider} | "
        f"approval={config.approval_mode}"
    )
    print("Type /help for commands. Type 'exit' or /exit to stop.")


def render_tool_events(events: Iterable[dict]) -> None:
    """Display tool activity in a visually distinct block."""
    for event in events:
        args = event.get("args", {})
        print("[tool]")
        print(f"  name: {event.get('tool_name', 'unknown')}")
        print(f"  args: {args}")
        print(f"  status: {event.get('status', 'unknown')}")
        if "result" in event:
            print(f"  result: {event['result']}")


def render_assistant_text(text: str) -> None:
    """Render the assistant response body."""
    if text:
        print(f"assistant> {text}")


def render_status(status: str) -> None:
    """Render a final task status line."""
    print(f"[status] {status}")


def render_error(message: str) -> None:
    """Render an error message distinctly."""
    print(f"[error] {message}")
