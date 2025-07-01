# src/rachel/clients/shallow/loader.py

from rachel.core.config import get_config


def _lazy_import_hf():
    from .hf_causal import HuggingFaceCausalClient
    return HuggingFaceCausalClient

def _lazy_import_gguf():
    from .llama_cpp import LlamaCppClient
    return LlamaCppClient


SHALLOW_CLIENT_MAP = {
    "hf-causal": _lazy_import_hf,
    "gguf": _lazy_import_gguf,
}


def get_shallow_llm():
    backend_name = get_config().model.shallow_LLM.backend
    try:
        ClientClass = SHALLOW_CLIENT_MAP[backend_name]()
        return ClientClass()
    except KeyError:
        raise ValueError(
            f"❌ Unknown shallow LLM backend: '{backend_name}'. "
            f"Valid options: {list(SHALLOW_CLIENT_MAP.keys())}"
        )
