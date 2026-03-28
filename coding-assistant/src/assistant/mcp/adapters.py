"""Helpers for normalizing MCP SDK tool metadata and results."""

from __future__ import annotations

from typing import Any


def normalize_tool_metadata(tool: Any, server_name: str) -> dict:
    """Convert an MCP SDK tool object into the local metadata shape."""
    if isinstance(tool, dict):
        name = tool.get("name", "")
        description = tool.get("description", "")
        input_schema = tool.get("input_schema", {})
    else:
        name = getattr(tool, "name", "")
        description = getattr(tool, "description", "") or ""
        input_schema = getattr(tool, "input_schema", {}) or {}

    return {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "server_name": server_name,
    }


def normalize_tool_result(result: Any) -> Any:
    """Return plain Python data from an MCP result payload."""
    content = getattr(result, "content", None)
    if content is None:
        return result

    if not isinstance(content, list):
        return content

    normalized: list[Any] = []
    for item in content:
        if isinstance(item, dict) and "text" in item:
            normalized.append(item["text"])
            continue

        text = getattr(item, "text", None)
        if text is not None:
            normalized.append(text)
            continue

        normalized.append(str(item))

    if len(normalized) == 1:
        return normalized[0]
    return normalized
