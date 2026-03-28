"""Execution helpers for running assistant tools."""

from assistant.tools.registry import TOOL_REGISTRY


def invoke_tool(name: str, args: dict) -> str:
    """Invoke a registered tool by name and return its result as a string."""
    if name not in TOOL_REGISTRY:
        return f"[error] unknown tool: {name}"
    try:
        result = TOOL_REGISTRY[name](**args)
        return str(result)
    except Exception as e:
        return f"[error] tool {name} failed: {e}"
