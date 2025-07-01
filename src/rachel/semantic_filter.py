import time
from typing import Optional
import numpy as np
from sentence_transformers import util

from rachel.clients.semantic.loader import get_semantic_filter
from rachel.core.config import get_config
from rachel.utils.metrics import record_metrics
from rachel.utils.common import debug
from rachel.runtime.runtime import semantic_lock, semantic_window


class SemanticFilter:
    def __init__(self):
        self._embedding_client = get_semantic_filter()
        cfg = get_config().model.semantic

        self.similarity_threshold: float = cfg.similarity_threshold
        self.context_window_seconds: float = cfg.context_minutes * 60

    def is_duplicate(self, text: str, now: Optional[float] = None) -> bool:
        t0 = time.time()
        now = now or t0

        vec = self._embedding_client.embed(text)

        with semantic_lock:
            recent = [(v, ts) for (v, ts) in semantic_window if now - ts < self.context_window_seconds]
            recent_vectors = [v for (v, _) in recent]

            is_dup = False
            if recent_vectors:
                sims = util.cos_sim(vec, recent_vectors)[0]
                if float(sims.max()) > self.similarity_threshold:
                    debug(f"[SemanticFilter] Duplicate detected (sim={float(sims.max()):.3f}): {text}")
                    is_dup = True

            if not is_dup:
                semantic_window.append((vec, now))

        record_metrics("semantic-dedup", t0, segment_count=len(recent_vectors))
        return is_dup
