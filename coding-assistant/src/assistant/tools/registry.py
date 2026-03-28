"""Registry for available assistant tools."""

from typing import Callable

TOOL_REGISTRY: dict[str, Callable] = {}


def register_tool(name: str, fn: Callable) -> None:
    TOOL_REGISTRY[name] = fn


def load_rag_tool() -> None:
    """Import docs_search from rag_server and register it as 'search_docs'."""
    import os
    import sys

    # rag_server/ is a sibling of src/ under coding-assistant/
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from rag_server.server import docs_search  # noqa: PLC0415

    register_tool("search_docs", lambda query: docs_search(query, top_k=5))
