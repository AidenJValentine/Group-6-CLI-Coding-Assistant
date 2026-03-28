"""Thin wrapper around litellm.completion() returning a normalized response dict."""

import os

import litellm


def call_llm(
    model: str,
    messages: list[dict],
    tools: list[dict] | None = None,
    stream: bool = False,
    api_key: str | None = None,
) -> dict:
    """Call any LiteLLM-supported model and return a normalized response.

    Returns:
        {
            "text":          str | None   — assistant text content
            "tool_calls":    list[dict]   — tool calls requested (empty list if none)
            "finish_reason": str          — "stop" | "tool_calls" | "length" | "error"
            "raw":           object       — raw LiteLLM ModelResponse
        }
    """
    if model.startswith("openrouter/"):
        key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        os.environ["OPENROUTER_API_KEY"] = key

    kwargs: dict = {"model": model, "messages": messages, "stream": stream}
    if tools:
        kwargs["tools"] = tools

    response = litellm.completion(**kwargs)

    message = response.choices[0].message
    finish_reason = response.choices[0].finish_reason or "stop"

    text = message.content  # may be None when the response is tool-calls only

    raw_tool_calls = getattr(message, "tool_calls", None) or []
    tool_calls = [
        {
            "id": tc.id,
            "type": tc.type,
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments,
            },
        }
        for tc in raw_tool_calls
    ]

    # model_dump() produces the exact dict format LiteLLM/OpenAI expect when
    # the message is replayed in subsequent turns (tool_calls, content, role).
    message_dict = message.model_dump()

    return {
        "text": text,
        "tool_calls": tool_calls,
        "finish_reason": finish_reason,
        "raw": response,
        "message_dict": message_dict,
    }
