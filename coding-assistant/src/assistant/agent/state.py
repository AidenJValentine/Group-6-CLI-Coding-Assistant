"""AgentState definition for the LangGraph-based assistant loop."""

from collections.abc import Callable
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """Shared LangGraph state for the Milestone 2 assistant flow."""

    original_task: str
    messages: list[dict]
    iteration_count: int
    max_iterations: int
    execution_mode: str
    tool_history: list[dict]
    plan: list[dict]
    final_answer: str
    status: str
    approval_mode: str
    pending_tool_call: dict | None
    latest_events: list[dict]
    step_results: list[dict]
    current_step: dict
    slash_command: str
    help_text: str
    exit_requested: bool
    provider: Any
    approval_handler: Callable[[dict], bool]
