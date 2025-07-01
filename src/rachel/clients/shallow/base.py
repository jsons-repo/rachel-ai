# clients/shallow/clients/base.py
from abc import ABC, abstractmethod

class ShallowLLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass