"""Run the assistant CLI from the local source tree."""

import argparse
from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Ensure UTF-8 output on Windows terminals that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env from repo root (two levels above coding-assistant/src/)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _REPO_ROOT / ".env"
if _ENV_FILE.exists():
    import os
    with open(_ENV_FILE) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

from assistant.cli.app import run_cli
from assistant.config import RuntimeConfig, get_openrouter_models


def parse_args() -> RuntimeConfig:
    """Parse CLI flags into runtime configuration."""
    parser = argparse.ArgumentParser(description="Run the AI coding assistant.")
    parser.add_argument("--provider", default="mock")
    parser.add_argument("--agent-model", default="mock-agent")
    parser.add_argument("--executor-model", default="mock-executor")
    parser.add_argument("--mode", choices=["debug", "build"], default="debug")
    parser.add_argument("--approval-mode", choices=["confirm", "auto"], default="confirm")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--openrouter-key", default=None, help="OpenRouter API key (falls back to OPENROUTER_API_KEY env var)")
    parser.add_argument("--list-models", action="store_true", help="Print supported OpenRouter model strings and exit")
    args = parser.parse_args()

    if args.list_models:
        print("Supported OpenRouter models:")
        for m in get_openrouter_models():
            print(f"  {m}")
        sys.exit(0)

    return RuntimeConfig(
        provider=args.provider,
        agent_model=args.agent_model,
        executor_model=args.executor_model,
        execution_mode=args.mode,
        approval_mode=args.approval_mode,
        max_iterations=args.max_iterations,
        openrouter_api_key=args.openrouter_key,
    )


def main() -> None:
    """Start the command-line interface."""
    run_cli(parse_args())


if __name__ == "__main__":
    main()
