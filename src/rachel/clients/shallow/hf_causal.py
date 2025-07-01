import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from huggingface_hub import snapshot_download
from peft import PeftModel
from pathlib import Path

from rachel.core.config import get_config
from rachel.utils.hardware import resolve_device_and_type
from rachel.utils.file_system import get_model_subdir_path, assert_model_path_exists
from rachel.utils.metrics import record_metrics
from rachel.utils.common import debug
from rachel.clients.shallow.base import ShallowLLMClient


class HuggingFaceCausalClient(ShallowLLMClient):
    def __init__(self):
        cfg = get_config()
        shallow_cfg = cfg.model.shallow_LLM

        # Normalize model name from repo for subdir path (decouples from adapter!)
        model_dir = get_model_subdir_path(
            cfg.shallow_root,
            shallow_cfg.backend,
            shallow_cfg.repo.split("/")[-1].replace(".", "_").replace("-", "_")
        )
        model_dir = Path(model_dir)

        resolved_device, resolved_type = resolve_device_and_type(
            shallow_cfg.device, shallow_cfg.compute_type
        )
        print(f"✅ Resolved shallow device={resolved_device}, type={resolved_type}")

        torch_dtype = (
            torch.float32 if resolved_device == "mps"
            else torch.float16 if resolved_type == "float16"
            else torch.float32
        )

        print(f"📦 Loading or syncing base model from: {shallow_cfg.repo} to: {model_dir}")

        base_model_path = snapshot_download(
            repo_id=shallow_cfg.repo,
            use_auth_token=cfg.hf_token,
            local_dir=model_dir,
            local_dir_use_symlinks=False,
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch_dtype,
            trust_remote_code=shallow_cfg.trust_remote_code,
        )

        # Adapter logic only if adapter + type are defined
        if shallow_cfg.adapter and shallow_cfg.adapter_type:
            adapter_dir = Path(cfg.adapter_root) / shallow_cfg.adapter_type / shallow_cfg.adapter / "adapter"
            adapter_tokenizer_dir = Path(cfg.adapter_root) / shallow_cfg.adapter_type / shallow_cfg.adapter / "tokenizer"

            assert_model_path_exists(adapter_dir)
            assert_model_path_exists(adapter_tokenizer_dir)

            print(f"✅ Applying {shallow_cfg.adapter_type.upper()} adapter from {adapter_dir}")
            base_model = PeftModel.from_pretrained(base_model, adapter_dir)
            self.tokenizer = AutoTokenizer.from_pretrained(adapter_tokenizer_dir)
        else:
            print("🧼 No adapter applied; using base tokenizer")
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)

        self.model = base_model

        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if resolved_device == "cuda" else -1,
            return_full_text=False,
        )

    def generate(self, prompt: str, **kwargs) -> str:
        shallow_cfg = get_config().model.shallow_LLM
        t0 = time.time()

        generation_kwargs = {
            "max_new_tokens": shallow_cfg.max_tokens,
            "do_sample": shallow_cfg.do_sample,
            "repetition_penalty": shallow_cfg.repetition_penalty,
        }

        if shallow_cfg.do_sample:
            generation_kwargs["temperature"] = shallow_cfg.temperature
            generation_kwargs["top_k"] = shallow_cfg.top_k
            generation_kwargs["top_p"] = shallow_cfg.top_p

        output = self.pipeline(prompt, **generation_kwargs)

        token_count = len(self.tokenizer(prompt)["input_ids"]) + shallow_cfg.max_tokens
        record_metrics(f'Shallow: {shallow_cfg.backend}', t0, tokens=token_count)
        debug("@HuggingFaceCausalClient: RAW OUTPUT:\n", output[0]["generated_text"])
        return output[0]["generated_text"]
