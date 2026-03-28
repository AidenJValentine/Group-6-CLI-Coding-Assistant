"""Dummy provider used while real model integrations are not implemented."""

from assistant.providers.base import BaseProvider


class DummyProvider(BaseProvider):
    """Minimal provider that returns a mock tool call first, then a final answer."""

    def generate(self, messages: list) -> dict:
        """Return a mock tool call on the first turn and a summary after the tool."""
        user_message = next(
            (
                message["content"]
                for message in reversed(messages)
                if message["role"] == "user"
            ),
            "",
        )
        tool_message = next(
            (message for message in reversed(messages) if message["role"] == "tool"),
            None,
        )

        if tool_message is not None:
            return {
                "text": (
                    "I finished the mocked tool step and can continue from here. "
                    f"Observed result: {tool_message['content']}"
                )
            }

        return {
            "text": f"I'll inspect this with a mocked tool first: {user_message}",
            "tool_call": {
                "name": "stub_tool",
                "args": {"task": user_message},
            },
        }
