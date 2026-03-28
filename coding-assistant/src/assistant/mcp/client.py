"""MCP client implementation used by the assistant."""

from __future__ import annotations

import asyncio
from typing import Any

from assistant.mcp.adapters import normalize_tool_metadata, normalize_tool_result


class MCPClient:
    """Connect to configured MCP servers and expose a unified tool registry.

    Uses a fresh connection per operation so that asyncio event loops never
    hold dangling stdio_client async generators — which causes the anyio
    'Attempted to exit cancel scope in a different task' noise on shutdown.
    """

    def __init__(self, servers: dict[str, dict]):
        self.servers = servers
        self.tools: dict[str, dict] = {}

    async def connect_all(self) -> None:
        """Discover tools from every configured MCP server (one-shot per server)."""
        for server_name in self.servers:
            await self._discover(server_name)

    async def _discover(self, server_name: str) -> None:
        """Open a connection, list tools, then close — no dangling state."""
        config = self.servers.get(server_name)
        if config is None:
            raise ValueError(f"Unknown MCP server: {server_name}")

        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
        except ImportError as exc:
            raise RuntimeError(
                "MCP support requires the optional 'mcp' package to be installed."
            ) from exc

        try:
            params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=None,  # inherit full parent environment (API keys etc.)
            )
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    discovered = await session.list_tools()
        except Exception as exc:
            raise RuntimeError(
                f"Failed to connect to MCP server '{server_name}': {exc}"
            ) from exc

        for tool in getattr(discovered, "tools", discovered):
            metadata = normalize_tool_metadata(tool, server_name)
            self.tools[metadata["name"]] = metadata

    def list_tools(self) -> dict[str, dict]:
        """Return discovered tool metadata keyed by tool name."""
        return dict(self.tools)

    def invoke_tool(self, name: str, arguments: dict) -> Any:
        """Synchronously invoke a discovered tool via a fresh connection."""
        return asyncio.run(self._invoke(name, arguments))

    async def _invoke(self, name: str, arguments: dict) -> Any:
        metadata = self.tools.get(name)
        if metadata is None:
            raise ValueError(f"Unknown tool: {name}")

        server_name = metadata["server_name"]
        config = self.servers[server_name]

        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
        except ImportError as exc:
            raise RuntimeError(
                "MCP support requires the optional 'mcp' package to be installed."
            ) from exc

        try:
            params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=None,
            )
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)
        except Exception as exc:
            raise RuntimeError(
                f"Tool '{name}' failed on server '{server_name}': {exc}"
            ) from exc

        return normalize_tool_result(result)
