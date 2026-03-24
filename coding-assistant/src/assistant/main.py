"""Run the assistant CLI from the local source tree."""

from pathlib import Path
import sys


# When this file is executed directly, add ``src`` so ``assistant`` imports work.
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from assistant.cli.app import run_cli


def main() -> None:
    """Start the command-line interface."""
    # Keep the entry point small so CLI behavior stays in the CLI package.
    run_cli()


if __name__ == "__main__":
    # Running this module directly launches the REPL loop.
    main()
