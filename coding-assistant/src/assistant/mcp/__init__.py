"""MCP integration package for external protocol support."""

from assistant.mcp.client import MCPClient
from assistant.mcp.server_config import MCP_SERVERS, load_mcp_servers

__all__ = ["MCPClient", "MCP_SERVERS", "load_mcp_servers"]
