"""Configuration definitions for the coding assistant."""

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeConfig:
    """Runtime settings for the Milestone 2 CLI skeleton."""

    provider: str = "mock"
    agent_model: str = "mock-agent"
    executor_model: str = "mock-executor"
    execution_mode: str = "debug"
    approval_mode: str = "confirm"
    max_iterations: int = 3
