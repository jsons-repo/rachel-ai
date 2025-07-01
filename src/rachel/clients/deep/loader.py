
from rachel.core.config import get_config

cfg = get_config()

def _lazy_import_openai():
    from .open_ai import OpenAIDeepClient
    return OpenAIDeepClient

DEEP_BACKEND_MAP = {
    "openai": _lazy_import_openai,
}

def get_deep_llm():
    try:
        BackendClass = DEEP_BACKEND_MAP[cfg.model.deep_LLM.client]()
        return BackendClass()
    except KeyError:
        raise ValueError(
            f"❌ Unknown deep backend: '{cfg.model.deep_LLM.client}'. "
            f"Valid options: {list(DEEP_BACKEND_MAP.keys())}"
        )
