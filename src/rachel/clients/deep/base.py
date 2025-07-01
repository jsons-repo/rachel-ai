# src/rachel/clients/deep/base.py

from abc import ABC, abstractmethod

class DeepLLMClient(ABC):
    @abstractmethod
    def send(self, prompt: str) -> str:
        """Send a prompt to the deep LLM and return the response string."""
        pass
