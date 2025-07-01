import time, psutil

def record_metrics(label: str, started_at: float, audio_duration: float = None, segment_count: int = None, tokens: int = None):
    elapsed = time.time() - started_at
    cpu = psutil.Process().cpu_percent(interval=0.1)
    mem = psutil.Process().memory_info().rss / 1e6

    rtf = (elapsed / audio_duration) if audio_duration else None
    print(f"\n⏱️ MODEL INFERNCE [{label}] time={elapsed:.2f}s | cpu={cpu:.1f}% | mem={mem:.1f}MB", end="")

    if audio_duration:
        print(f" | audio={audio_duration:.2f}s | RTF={rtf:.2f}x", end="")
    if segment_count is not None:
        print(f" | segments={segment_count}", end="")
    if tokens is not None:
        print(f" | tokens={tokens}", end="")

    print("\n")