"""Dummy provider used while real model integrations are not implemented."""

from assistant.providers.base import BaseProvider


class DummyProvider(BaseProvider):
    """Minimal provider that always returns a fixed response."""

    def generate(self, messages: list) -> dict:
        """Return a static response while real providers are not implemented."""
        return {"text": "This is a dummy response"}
