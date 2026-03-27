"""AgentState definition and initialization helpers for the LangGraph agent loop."""

import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    # Core task context
    original_task: str
    messages: list[dict]          # Full conversation history (role/content dicts)

    # Iteration control
    iteration_count: int
    max_iterations: int

    # Mode — "debug" (ReAct) or "build" (plan-and-execute)
    execution_mode: str

    # Tool tracking — uses operator.add reducer so parallel fan-out results accumulate
    tool_history: Annotated[list[dict], operator.add]

    # Build-mode: current step being executed (set by fan_out_plan via Send())
    current_step: dict

    # Build-mode plan
    # Each entry: {"id": str, "step": str, "depends_on": list[str]}
    # MVP: depends_on is always [] (all steps treated as independent).
    # Post-MVP: planner emits real dependency edges; executor and synthesizer
    # respect ordering.
    plan: list[dict]

    # Output
    final_answer: str
    status: str                   # "running" | "completed" | "failed" | "cancelled"


def make_initial_state(
    execution_mode: str = "debug",
    max_iterations: int = 10,
) -> AgentState:
    """Return a valid AgentState with safe defaults for a new session."""
    return AgentState(
        original_task="",
        messages=[],
        iteration_count=0,
        max_iterations=max_iterations,
        execution_mode=execution_mode,
        tool_history=[],
        current_step={},
        plan=[],
        final_answer="",
        status="running",
    )
