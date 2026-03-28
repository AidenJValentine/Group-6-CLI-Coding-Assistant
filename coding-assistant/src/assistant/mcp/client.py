"""MCP client implementation used by the assistant."""

from __future__ import annotations

import asyncio
from typing import Any

from assistant.mcp.adapters import normalize_tool_metadata, normalize_tool_result


class MCPClient:
    """Connect to configured MCP servers and expose a unified tool registry."""

    def __init__(self, servers: dict[str, dict]):
        self.servers = servers
        self.sessions: dict[str, Any] = {}
        self.tools: dict[str, dict] = {}

    async def connect_all(self) -> None:
        """Connect to every configured MCP server."""
        for server_name in self.servers:
            await self._connect(server_name)

    async def _connect(self, server_name: str):
        if server_name in self.sessions:
            return self.sessions[server_name]

        config = self.servers.get(server_name)
        if config is None:
            raise ValueError(f"Unknown MCP server: {server_name}")

        try:
            from mcp.client import ClientSession
            from mcp.client.stdio import stdio_client
        except ImportError as exc:
            raise RuntimeError(
                "MCP support requires the optional 'mcp' package to be installed."
            ) from exc

        try:
            transport = await stdio_client(
                command=config["command"],
                args=config.get("args", []),
            )
            session = await ClientSession(transport).__aenter__()
            discovered = await session.list_tools()
        except Exception as exc:
            raise RuntimeError(f"Failed to connect to MCP server '{server_name}': {exc}") from exc

        tools = getattr(discovered, "tools", discovered)
        self.sessions[server_name] = session

        for tool in tools:
            metadata = normalize_tool_metadata(tool, server_name)
            self.tools[metadata["name"]] = metadata

        return session

    def list_tools(self) -> dict[str, dict]:
        """Return discovered tool metadata keyed by tool name."""
        return dict(self.tools)

    def invoke_tool(self, name: str, arguments: dict) -> Any:
        """Synchronously invoke a discovered tool."""
        return asyncio.run(self._invoke(name, arguments))

    async def _invoke(self, name: str, arguments: dict) -> Any:
        metadata = self.tools.get(name)
        if metadata is None:
            raise ValueError(f"Unknown tool: {name}")

        server_name = metadata["server_name"]
        session = await self._connect(server_name)

        try:
            result = await session.call_tool(name, arguments)
        except Exception as exc:
            raise RuntimeError(
                f"Tool '{name}' failed on server '{server_name}': {exc}"
            ) from exc

        return normalize_tool_result(result)
