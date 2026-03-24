"""Execution helpers for running assistant tools."""

from assistant.tools.registry import TOOL_REGISTRY


def invoke_tool(name: str, args: dict) -> str:
    """Invoke a registered tool and return a placeholder result."""
    # Later, this function can route calls to local Python tools or MCP tools.
    # The registry lookup stays simple now so the interface is easy to extend.
    _tool = TOOL_REGISTRY.get(name)
    _args = args

    return "stub tool result"
