# src/rachel/clients/semantic/base.py

from abc import ABC, abstractmethod
import numpy as np

class SemanticEmbeddingClient(ABC):
    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """Return a normalized embedding vector for the given text."""
        pass
