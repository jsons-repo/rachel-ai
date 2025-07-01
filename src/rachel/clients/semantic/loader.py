# src/rachel/clients/semantic/loader.py

from rachel.core.config import get_config


def _lazy_import_sentence():
    from .sentence_transformer import SentenceTransformerClient
    return SentenceTransformerClient


EMBEDDING_CLIENT_MAP = {
    "sentence-transformer": _lazy_import_sentence,
}


def get_semantic_filter():
    backend_name = get_config().model.semantic.backend
    try:
        ClientClass = EMBEDDING_CLIENT_MAP[backend_name]()
        return ClientClass()
    except KeyError:
        raise ValueError(
            f"❌ Unknown embedding backend: '{backend_name}'. "
            f"Valid options: {list(EMBEDDING_CLIENT_MAP.keys())}"
        )
