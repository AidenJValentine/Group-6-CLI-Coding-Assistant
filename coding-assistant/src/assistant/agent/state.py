"""AgentState definition for the LangGraph-based assistant loop."""

from typing import TypedDict


class AgentState(TypedDict):
    # Core task context
    original_task: str
    messages: list[dict]          # Full conversation history (role/content dicts)

    # Iteration control
    iteration_count: int
    max_iterations: int

    # Mode — "debug" (ReAct) or "build" (plan-and-execute)
    execution_mode: str

    # Tool tracking
    tool_history: list[dict]      # Record of every tool call and its result

    # Build-mode plan
    # Each entry: {"id": str, "step": str, "depends_on": list[str]}
    # MVP: depends_on is always [] (all steps treated as independent).
    # Post-MVP: planner emits real dependency edges; executor and synthesizer
    # respect ordering.
    plan: list[dict]

    # Output
    final_answer: str
    status: str                   # "running" | "completed" | "failed" | "cancelled"
