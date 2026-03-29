"""Rendering helpers for terminal output — powered by rich."""

import os
import sys
import time
from collections.abc import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from assistant.config import RuntimeConfig

console = Console(highlight=False)

_FILE_OPS = {"write_file", "edit_file", "delete_file", "create_directory"}
_FILE_ICONS = {
    "write_file": "📝",
    "edit_file": "✏️ ",
    "delete_file": "🗑️ ",
    "create_directory": "📁",
}


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


def render_mcp_servers(server_names: list[str]) -> None:
    """Show which MCP servers connected at boot."""
    for name in server_names:
        console.print(f"[cyan]◆[/cyan] [dim]{name:<12}[/dim] connected")
    if server_names:
        console.print()


def render_thinking() -> None:
    """Print a transient 'thinking' indicator."""
    if sys.stdout.isatty():
        sys.stdout.write("  ◌ thinking...\r")
        sys.stdout.flush()
    else:
        console.print("[dim]  ◌ thinking...[/dim]")


def render_clear_thinking() -> None:
    """Erase the thinking indicator (TTY only)."""
    if sys.stdout.isatty():
        sys.stdout.write("                    \r")
        sys.stdout.flush()


def render_tool_call(name: str, args: dict) -> float:
    """Show a tool invocation. Returns start time for elapsed tracking."""
    start = time.time()
    if name in _FILE_OPS:
        icon = _FILE_ICONS.get(name, "📄")
        path = args.get("path", args.get("name", ""))
        content = args.get("content", "")
        size_str = f"  [dim]({len(content) / 1024:.1f}kb)[/dim]" if content else ""
        console.print(
            f"{icon} [bold]{name:<20}[/bold] [cyan]{path}[/cyan]{size_str}"
        )
    else:
        summary = ""
        for v in args.values():
            if isinstance(v, str):
                trimmed = v[:70] + ("..." if len(v) > 70 else "")
                summary = f'"{trimmed}"'
                break
        console.print(
            f"[bold yellow]⚡[/bold yellow] [bold]{name}[/bold]  [dim]{summary}[/dim]"
        )
    return start


def render_tool_result(name: str, result: str, start_time: float | None = None) -> None:
    """Show a compact tool result summary."""
    if name in _FILE_OPS:
        return  # file op display is self-contained in render_tool_call
    elapsed = f", {time.time() - start_time:.1f}s" if start_time is not None else ""
    size = len(str(result))
    console.print(
        f"  [bold green]✓[/bold green] [dim]done  ({size:,} chars{elapsed})[/dim]\n"
    )


def render_tool_events(events: Iterable[dict]) -> None:
    """No-op: tool calls are rendered live in tool_executor."""
    pass


def render_assistant(text: str) -> None:
    """Render the assistant response in a styled panel."""
    if text:
        console.print(
            Panel(
                text,
                border_style="dim cyan",
                title="[bold cyan]axiom[/bold cyan]",
                title_align="left",
            )
        )


render_assistant_text = render_assistant


def render_status(status: str, iterations: int = 0, elapsed: float | None = None) -> None:
    """Render a final task status line."""
    color = "green" if status == "completed" else "red"
    iter_part = f"  [dim]{iterations} iterations[/dim]" if iterations else ""
    time_part = f"  [dim]{elapsed:.1f}s[/dim]" if elapsed is not None else ""
    console.print(f"[{color}]●[/{color}] [bold {color}]{status}[/bold {color}]{iter_part}{time_part}\n")


def render_error(message: str) -> None:
    """Render an error message distinctly."""
    console.print(f"[bold red]✗ error[/bold red] [red]{message}[/red]")


def render_result(state: dict, elapsed: float | None = None) -> None:
    """Print final answer then status line. Tool calls already rendered live."""
    render_assistant(state.get("final_answer", ""))
    render_status(
        state.get("status", "unknown"),
        state.get("iteration_count", 0),
        elapsed=elapsed,
    )
