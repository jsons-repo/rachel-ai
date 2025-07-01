# src/rachel/clients/semantic/sentence_transformer.py

from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
from pathlib import Path
import numpy as np

from rachel.core.config import get_config
from rachel.utils.file_system import get_model_subdir_path, assert_model_path_exists
from .base import SemanticEmbeddingClient


class SentenceTransformerClient(SemanticEmbeddingClient):
    def __init__(self):
        cfg = get_config()
        semantic_cfg = cfg.model.semantic

        model_path = Path(get_model_subdir_path(
            cfg.embedded_filter_root,
            semantic_cfg.backend,
            semantic_cfg.name
        ))

        if not model_path.exists():
            print(f"📦 Downloading semantic model {semantic_cfg.repo} → {model_path}")
            snapshot_download(
                repo_id=semantic_cfg.repo,
                local_dir=model_path,
                local_dir_use_symlinks=False
            )

        assert_model_path_exists(model_path)
        
        print(f"✅ Loading SentenceTransformer from: {model_path}")
        self.model = SentenceTransformer(str(model_path), local_files_only=True)

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)
