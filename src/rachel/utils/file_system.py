# src/rachel/utils/filesystem.py

import os
import re

def get_model_subdir_path(root_dir: str, backend: str, filename: str = None) -> str:
    """
    Safely construct a path for snapshot_download() or model loading.

    Args:
        root_dir (str): Root directory for models (e.g., ~/.rachel/models/shallow).
        backend (str): Subdir under root for this backend (e.g., "gguf").
        filename (str, optional): Specific model file name (e.g., model.gguf). If None, returns just the dir.

    Returns:
        str: Fully qualified path to model dir or file.
    """
    # Expand root and validate backend
    root_dir = os.path.realpath(os.path.expanduser(root_dir))
    if not isinstance(backend, str) or not backend:
        raise ValueError("Backend name must be a non-empty string")
    if not re.match(r"^[a-zA-Z0-9_-]+$", backend):
        raise ValueError(f"Unsafe backend name: {backend}")

    base_path = os.path.join(root_dir, backend)

    if filename:
        if not isinstance(filename, str) or not re.match(r"^[a-zA-Z0-9_.-]+$", filename):
            raise ValueError(f"Unsafe filename: {filename}")
        return os.path.join(base_path, filename)
    
    print("get_model_subdir_path:returning base_path:", base_path)
    return base_path


def assert_model_path_exists(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model path not found: {model_path}")