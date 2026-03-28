"""Planner: produces a dependency-aware step list from a task description."""

import json
import re

from assistant.config import load_provider_config
from assistant.providers.litellm_client import call_llm

PLANNER_PROMPT = """You are a planning assistant. Break the following task into independent steps that can be executed in parallel.

Return ONLY a JSON array. Each element must have:
- "id": a short unique string (e.g. "step_1")
- "step": a clear description of what to do
- "depends_on": an empty list [] (MVP: all steps are independent)

Example output:
[
  {{"id": "step_1", "step": "Read the file src/main.py", "depends_on": []}},
  {{"id": "step_2", "step": "Search for Python async patterns", "depends_on": []}}
]

Task: {task}"""


def make_plan(task: str) -> list[dict]:
    config = load_provider_config()
    result = call_llm(
        config["agent_model"],
        [{"role": "user", "content": PLANNER_PROMPT.format(task=task)}],
    )
    text = result["text"]

    # Find the outermost [...] by tracking bracket depth — avoids greedy-match
    # issues when the model adds extra text before or after the array.
    start = text.find("[")
    if start == -1:
        raise ValueError(f"Planner did not return a JSON array. Got: {text}")

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])

    raise ValueError(f"Planner returned unbalanced JSON. Got: {text}")
