# clients/shallow/llama_cpp.py

import os
import time
from llama_cpp import Llama
from huggingface_hub import snapshot_download

from rachel.core.config import get_config
from rachel.utils.metrics import record_metrics
from rachel.utils.file_system import get_model_subdir_path, assert_model_path_exists
from rachel.clients.shallow.base import ShallowLLMClient


class LlamaCppClient(ShallowLLMClient):
    def __init__(self):
        cfg = get_config()
        shallow_cfg = cfg.model.shallow_LLM

        model_dir = get_model_subdir_path(
            get_config().shallow_root,
            backend=shallow_cfg.backend,
            filename=shallow_cfg.name
        )

        print(f"📦 Downloading or loading GGUF model from: {shallow_cfg.repo} to: {model_dir}")
        model_path = snapshot_download(
            repo_id=shallow_cfg.repo,
            use_auth_token=cfg.hf_token,
            local_dir=model_dir
        )

        assert_model_path_exists(model_path)

        # Find the first .gguf file in the downloaded dir
        gguf_files = [f for f in os.listdir(model_path) if f.endswith(".gguf")]
        if not gguf_files:
            raise FileNotFoundError(f"No GGUF model file found in {model_path}")

        full_model_path = os.path.join(model_path, gguf_files[0])
        print(f"🧠 Loading GGUF model from: {full_model_path}")

        self.llm = Llama(model_path=full_model_path, n_ctx=shallow_cfg.ctx_window_tokens)

    def generate(self, prompt: str, **kwargs) -> str:
        cfg = get_config()
        shallow_cfg = cfg.model.shallow_LLM

        t0 = time.time()
        result = self.llm(prompt, max_tokens=shallow_cfg.max_tokens)
        record_metrics(shallow_cfg.backend, t0, tokens=result["usage"]["total_tokens"])
        return result["choices"][0]["text"]
