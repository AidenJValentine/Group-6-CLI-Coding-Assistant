"""Execution helpers for running assistant tools."""

from assistant.tools.registry import TOOL_REGISTRY


def invoke_tool(name: str, args: dict) -> str:
    """Invoke a registered tool and return a placeholder result."""
    tool = TOOL_REGISTRY.get(name)
    if tool is None:
        return f"Tool '{name}' is not registered."

    return (
        f"Mocked execution of {name}: "
        f"{tool['description']} | args={args}"
    )
