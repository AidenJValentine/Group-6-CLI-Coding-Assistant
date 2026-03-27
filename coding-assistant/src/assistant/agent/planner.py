"""Planning components for agent task execution."""


def build_mock_plan(task: str) -> list[dict]:
    """Return a one-step mock plan for Milestone 2 build-mode demos."""
    return [
        {
            "id": "1",
            "step": f"Mock implementation plan for: {task}",
            "depends_on": [],
        }
    ]
