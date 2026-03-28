"""CLI application loop for reading input and printing responses."""

import os

from assistant.agent.loop import run_agent
from assistant.cli.renderer import (
    console,
    render_banner,
    render_error,
    render_result,
)
from assistant.config import RuntimeConfig, get_openrouter_models

_MOCK_MODELS = {"mock-agent", "mock-executor", ""}


def _prompt_for_model(config: RuntimeConfig) -> None:
    """If no real model is configured, ask the user how they want to connect."""
    if config.agent_model not in _MOCK_MODELS:
        # Still check for missing Tavily key even when model is pre-configured
        _prompt_for_tavily()
        return

    console.print("\n[bold]No model configured.[/bold] How do you want to connect?")
    console.print("  [cyan]1.[/cyan] Use local Ollama (requires ollama running)")
    console.print("  [cyan]2.[/cyan] Enter OpenRouter API key [dim](get one free at openrouter.ai)[/dim]")
    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        config.agent_model = "ollama/llama3.2"
        config.executor_model = "ollama/llama3.2"
        config.provider = "ollama"
    elif choice == "2":
        # Check if key already set; if not, prompt for it
        existing_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if existing_key:
            key = existing_key
            console.print("[dim]  Using OPENROUTER_API_KEY from environment.[/dim]")
        else:
            key = input("Enter your OpenRouter API key (get one free at openrouter.ai): ").strip()
            if key:
                config.openrouter_api_key = key
                os.environ["OPENROUTER_API_KEY"] = key
            else:
                console.print("[yellow]No key entered — defaulting to Ollama.[/yellow]")
                config.agent_model = "ollama/llama3.2"
                config.executor_model = "ollama/llama3.2"
                config.provider = "ollama"
                _prompt_for_tavily()
                return

        models = get_openrouter_models()
        console.print("\n[bold]Available models:[/bold]")
        for i, m in enumerate(models, 1):
            console.print(f"  [cyan]{i}.[/cyan] {m}")
        idx = input(f"Pick a model (1-{len(models)}): ").strip()
        try:
            config.agent_model = models[int(idx) - 1]
        except (ValueError, IndexError):
            config.agent_model = models[0]
            console.print(f"[yellow]Invalid choice, defaulting to {config.agent_model}[/yellow]")
        config.executor_model = config.agent_model
        config.provider = "openrouter"

    _prompt_for_tavily()


def _prompt_for_tavily() -> None:
    """If TAVILY_API_KEY is not set, prompt for it or remove tavily_search from tools."""
    if os.environ.get("TAVILY_API_KEY", "").strip():
        return  # already configured

    console.print("\n[dim]Tavily web search is available (tavily.com).[/dim]")
    key = input("Enter your Tavily API key (or press Enter to skip): ").strip()

    if key:
        os.environ["TAVILY_API_KEY"] = key
    else:
        # Remove tavily_search from the LLM tool schema so it won't try to call it
        from assistant.agent.loop import MOCK_TOOLS
        to_remove = [
            t for t in MOCK_TOOLS
            if t.get("function", {}).get("name") == "tavily_search"
        ]
        for t in to_remove:
            MOCK_TOOLS.remove(t)
        console.print("[dim]  Web search disabled.[/dim]")


def run_cli(config: RuntimeConfig) -> None:
    """Run the assistant REPL."""
    _prompt_for_model(config)
    render_banner(config)

    while True:
        try:
            mode_color = "red" if config.execution_mode == "debug" else "blue"
            prompt_text = f"[{config.execution_mode}] > "
            user_input = console.input(f"[bold {mode_color}]{prompt_text}[/bold {mode_color}]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        normalized_input = user_input.strip()
        if not normalized_input:
            continue
        if normalized_input.lower() in {"/exit", "/quit", "exit", "quit"}:
            console.print("[dim]Goodbye![/dim]")
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
