import time
from openai import OpenAI
from rachel.core.config import get_config
from rachel.clients.deep.base import DeepLLMClient
from rachel.utils.metrics import record_metrics

class OpenAIDeepClient(DeepLLMClient):

    def send(self, prompt: str) -> str:
        cfg = get_config()

        if not cfg.deep_api_key:
            raise RuntimeError("❌ Missing deep_api_key — check your config.yaml or get_config() logic")

        client = OpenAI(api_key=cfg.deep_api_key)

        start = time.time()
        response = client.chat.completions.create(
            model=cfg.model.deep_LLM.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        duration = time.time() - start

        # Estimate token count (OpenAI client may provide better tools for this, but we assume worst-case)
        token_count = len(prompt.split()) + 512  # crude est: input + expected output

        record_metrics(f"Deep: OpenAI/{cfg.model.deep_LLM.name}", start, tokens=token_count)
        print(f"🧠 OpenAI response time: {duration:.2f}s")

        return response.choices[0].message.content
