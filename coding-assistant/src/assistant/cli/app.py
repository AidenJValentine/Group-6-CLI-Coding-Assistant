"""CLI application loop for reading input and printing responses."""

import os

from assistant.agent.loop import run_agent
from assistant.cli.renderer import render_banner, render_error, render_result
from assistant.config import RuntimeConfig, get_openrouter_models

_MOCK_MODELS = {"mock-agent", "mock-executor", ""}


def _prompt_for_model(config: RuntimeConfig) -> None:
    """If no real model is configured, ask the user how they want to connect."""
    if config.agent_model not in _MOCK_MODELS:
        return

    print("No model configured. Options:")
    print("  1. Use local Ollama (requires ollama running)")
    print("  2. Enter OpenRouter API key (get one free at openrouter.ai)")
    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        config.agent_model = "ollama/llama3.2"
        config.executor_model = "ollama/llama3.2"
        config.provider = "ollama"
    elif choice == "2":
        key = input("OpenRouter API key: ").strip()
        if key:
            config.openrouter_api_key = key
            os.environ["OPENROUTER_API_KEY"] = key
        models = get_openrouter_models()
        print("Available models:")
        for i, m in enumerate(models, 1):
            print(f"  {i}. {m}")
        idx = input(f"Pick a model (1-{len(models)}): ").strip()
        try:
            config.agent_model = models[int(idx) - 1]
            config.executor_model = config.agent_model
            config.provider = "openrouter"
        except (ValueError, IndexError):
            config.agent_model = models[0]
            config.executor_model = models[0]
            config.provider = "openrouter"
            print(f"Invalid choice, defaulting to {config.agent_model}")


def run_cli(config: RuntimeConfig) -> None:
    """Run the assistant REPL."""
    _prompt_for_model(config)
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
