"""Run the assistant CLI from the local source tree."""

import argparse
from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from assistant.cli.app import run_cli
from assistant.config import RuntimeConfig


def parse_args() -> RuntimeConfig:
    """Parse CLI flags into runtime configuration."""
    parser = argparse.ArgumentParser(description="Run the AI coding assistant.")
    parser.add_argument("--provider", default="mock")
    parser.add_argument("--agent-model", default="mock-agent")
    parser.add_argument("--executor-model", default="mock-executor")
    parser.add_argument("--mode", choices=["debug", "build"], default="debug")
    parser.add_argument("--approval-mode", choices=["confirm", "auto"], default="confirm")
    parser.add_argument("--max-iterations", type=int, default=3)
    args = parser.parse_args()
    return RuntimeConfig(
        provider=args.provider,
        agent_model=args.agent_model,
        executor_model=args.executor_model,
        execution_mode=args.mode,
        approval_mode=args.approval_mode,
        max_iterations=args.max_iterations,
    )


def main() -> None:
    """Start the command-line interface."""
    run_cli(parse_args())


if __name__ == "__main__":
    main()
