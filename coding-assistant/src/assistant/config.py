"""Config loader for the coding assistant.

Priority order for each key:
  1. config.yaml (if it exists next to this file or in the working directory)
  2. Environment variables AGENT_MODEL / EXECUTOR_MODEL
  3. Hard-coded default: "ollama/llama3.2"
"""

import os
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_MODEL = "ollama/llama3.2"

# Look for config.yaml alongside this file first, then in cwd.
_CONFIG_SEARCH_PATHS = [
    Path(__file__).parent / "config.yaml",
    Path.cwd() / "config.yaml",
]


def _load_yaml(path: Path) -> dict:
    import yaml  # deferred — yaml may not be installed in all envs

    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_provider_config() -> dict:
    """Return config dict with at least agent_model and executor_model."""
    file_cfg: dict = {}
    for candidate in _CONFIG_SEARCH_PATHS:
        if candidate.exists():
            file_cfg = _load_yaml(candidate)
            break

    agent_model = (
        file_cfg.get("agent_model")
        or os.environ.get("AGENT_MODEL")
        or _DEFAULT_MODEL
    )
    executor_model = (
        file_cfg.get("executor_model")
        or os.environ.get("EXECUTOR_MODEL")
        or _DEFAULT_MODEL
    )

    return {"agent_model": agent_model, "executor_model": executor_model}


# ---------------------------------------------------------------------------
# RuntimeConfig — CLI startup settings (from CLI-Interface branch)
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RuntimeConfig:
    """Runtime settings passed from CLI flags to the agent loop."""

    provider: str = "mock"
    agent_model: str = "mock-agent"
    executor_model: str = "mock-executor"
    execution_mode: str = "debug"
    approval_mode: str = "confirm"
    max_iterations: int = 10
