"""Shared interfaces for assistant response providers."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Common interface for components that generate assistant responses."""

    @abstractmethod
    def generate(self, messages: list) -> dict:
        """Generate a response payload from a list of messages."""
        raise NotImplementedError
