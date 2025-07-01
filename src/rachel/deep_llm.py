# src/rachel/deep_api.py

import time
import json
import threading
import queue
from rachel.clients.deep.loader import get_deep_llm
from rachel.core.model import Flag, FlagSource, ShallowTranscriptContext
from rachel.core.types import SegmentStatus
from rachel.runtime.runtime import deep_queue, deep_queue_results, recent_flags_window, stop_signal
from rachel.utils.common import parse_deep_response, debug
from rachel.utils.print_out import print_deep_client_result, print_deep_client_inputs
from rachel.utils.prompts import generate_deep_prompt

is_processing = threading.Event()
is_processing.set()

llm_client = get_deep_llm()

def process_deep_queue():
    while not stop_signal.is_set():
        if not deep_queue.empty() and is_processing.is_set():
            try:
                shallow_context: ShallowTranscriptContext = deep_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            is_processing.clear()

            prompt = generate_deep_prompt(shallow_context, recent_flags_window)
            print_deep_client_inputs(shallow_context, prompt)

            try:
                start = time.time()
                raw = llm_client.send(prompt)
                duration = time.time() - start
                print_deep_client_result(raw, duration)

                flag = parse_deep_response(raw, prompt, shallow_context.current.id)
                if flag:
                    flags = shallow_context.current.flags or []
                    for i, f in enumerate(flags):
                        if f.source == FlagSource.SHALLOW and set(f.matches) == set(flag.matches):
                            flags[i] = flag
                            break
                    else:
                        flags.append(flag)

                    shallow_context.current.flags = flags
                    shallow_context.current.status = SegmentStatus.COMPLETE
                    recent_flags_window.append(flag)

                deep_queue_results.put(shallow_context)

            except Exception as e:
                print(f"❌ Error processing deep LLM request: {e}")
            finally:
                is_processing.set()
        else:
            time.sleep(0.2)
