"""Tool registry for assistant-exposed tools."""

from assistant.mcp.server_config import MCP_SERVERS

TOOL_REGISTRY = {}
MCP = None


def register_tool(name: str, fn):
    TOOL_REGISTRY[name] = fn


def load_all_tools():
    """Load tools from MCP servers and register them as callables."""
    if not MCP_SERVERS:
        return

    global MCP
    if MCP is None:
        from assistant.mcp.mcp_client import MCPClient

        MCP = MCPClient(MCP_SERVERS)

    import asyncio

    asyncio.run(MCP.connect_all())

    tools = MCP.list_tools()

    for tool_name in tools:
        if tool_name in TOOL_REGISTRY:
            continue  # don't overwrite in-process tools (e.g. search_docs)

        def make_tool(name):
            def tool_fn(**kwargs):
                return MCP.invoke_tool(name, kwargs)
            return tool_fn

        register_tool(tool_name, make_tool(tool_name))


def load_rag_tool():
    """Register the local docs search tool and all MCP server tools."""
    import os
    import sys

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from rag_server.server import search_docs  # noqa: PLC0415
        register_tool("search_docs", lambda query: search_docs(query, top_k=5))
    except ImportError:
        pass  # RAG deps not installed; search_docs simply won't be available

    # Always load MCP server tools (filesystem, tavily, etc.) on top of RAG
    load_all_tools()
