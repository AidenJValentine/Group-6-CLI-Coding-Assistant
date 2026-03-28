"""Rendering helpers for terminal output — powered by rich."""

from collections.abc import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from assistant.config import RuntimeConfig

console = Console()


def render_banner(config: RuntimeConfig) -> None:
    """Print a rich startup banner."""
    title = Text("AXIOM", style="bold cyan", justify="center")
    console.print(
        Panel(
            title,
            subtitle="[dim]autonomous coding assistant[/dim]",
            border_style="cyan",
        )
    )
    console.print(
        f"[dim]  mode=[/dim][cyan]{config.execution_mode}[/cyan]"
        f"[dim] | provider=[/dim][cyan]{config.provider}[/cyan]"
        f"[dim] | model=[/dim][cyan]{config.agent_model}[/cyan]"
    )
    console.print("[dim]  type /help for commands[/dim]\n")


def render_tool_call(name: str, args: dict) -> None:
    """Show a tool invocation before it runs."""
    console.print(f"\n[bold yellow]⚡ tool call[/bold yellow] [cyan]{name}[/cyan]")
    console.print(f"[dim]{args}[/dim]")


def render_tool_result(name: str, result: str) -> None:
    """Show a compact tool result summary."""
    console.print(
        f"[bold green]✓[/bold green] [dim]{name} returned {len(str(result))} chars[/dim]\n"
    )


def render_tool_events(events: Iterable[dict]) -> None:
    """Display all tool activity for a completed turn."""
    for event in events:
        name = event.get("tool") or event.get("tool_name", "unknown")
        args = event.get("args", {})
        result = event.get("result", "")
        render_tool_call(name, args)
        render_tool_result(name, result)


def render_assistant(text: str) -> None:
    """Render the assistant response in a styled panel."""
    if text:
        console.print(
            Panel(
                text,
                border_style="dim",
                title="[dim]assistant[/dim]",
                title_align="left",
            )
        )


# Keep legacy name used by render_result
render_assistant_text = render_assistant


def render_status(status: str, iterations: int = 0) -> None:
    """Render a final task status line."""
    color = "green" if status == "completed" else "red"
    iter_part = f" [dim]({iterations} iterations)[/dim]" if iterations else ""
    console.print(f"[{color}]● {status}[/{color}]{iter_part}\n")


def render_error(message: str) -> None:
    """Render an error message distinctly."""
    console.print(f"[bold red]✗ error[/bold red] [red]{message}[/red]")


def render_result(state: dict) -> None:
    """Print tool calls, then final answer, then status line."""
    render_tool_events(state.get("tool_history", []))
    render_assistant(state.get("final_answer", ""))
    render_status(
        state.get("status", "unknown"),
        state.get("iteration_count", 0),
    )
