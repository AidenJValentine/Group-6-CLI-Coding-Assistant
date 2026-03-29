"""MCP server configuration for the assistant."""

from __future__ import annotations

import os
import shlex
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _split_args(raw_args: str) -> list[str]:
    try:
        return [p for p in shlex.split(raw_args, posix=False) if p]
    except ValueError:
        return [part for part in raw_args.split() if part]


def _load_optional_server(prefix: str) -> dict | None:
    command = os.environ.get(f"{prefix}_COMMAND")
    if not command:
        return None

    return {
        "command": command,
        "args": _split_args(os.environ.get(f"{prefix}_ARGS", "")),
    }


def _load_rag_server() -> dict | None:
    command = os.environ.get("ASSISTANT_RAG_MCP_COMMAND")
    if not command:
        return None

    raw_args = os.environ.get("ASSISTANT_RAG_MCP_ARGS")
    if raw_args:
        args = _split_args(raw_args)
    else:
        args = [str(_project_root() / "rag_server" / "server.py")]

    # Always run the RAG server from the coding-assistant root so that
    # `python -m rag_server.server` resolves the package correctly regardless
    # of where the user launched axiom from.
    return {"command": command, "args": args, "cwd": str(_project_root())}


def load_mcp_servers() -> dict[str, dict]:
    """Load configured MCP servers from environment variables."""
    servers: dict[str, dict] = {}

    filesystem = _load_optional_server("ASSISTANT_FILESYSTEM_MCP")
    if filesystem:
        servers["filesystem"] = filesystem

    external = _load_optional_server("ASSISTANT_EXTERNAL_MCP")
    if external:
        servers["external"] = external

    rag = _load_rag_server()
    if rag:
        servers["rag"] = rag

    return servers


MCP_SERVERS: dict[str, dict] = load_mcp_servers()
