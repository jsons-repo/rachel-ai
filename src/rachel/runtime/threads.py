# src/rachel/runtime/threads.py

import threading
import logging

logger = logging.getLogger(__name__)

class ManagedThread:
    def __init__(self, target, name, stop_signal=None, args=(), kwargs=None):
        self.stop_signal = stop_signal or threading.Event()
        self.thread = threading.Thread(
            target=target,
            name=name,
            args=args,
            kwargs=kwargs or {}
        )
        self.thread.daemon = False  # Safe: ensures proper join() usage

    def start(self):
        self.thread.start()

    def stop(self, timeout=5):
        self.stop_signal.set()
        self.thread.join(timeout)
        if self.thread.is_alive():
            logger.warning(f"Thread {self.thread.name} didn't stop gracefully")

    def is_alive(self):
        return self.thread.is_alive()
