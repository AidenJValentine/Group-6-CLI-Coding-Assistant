"""Utilities for constructing agent messages."""


def build_initial_messages(task: str) -> list[dict]:
    """Create the initial message list for a new user task."""
    return [{"role": "user", "content": task}]
