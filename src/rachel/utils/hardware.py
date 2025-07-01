# src/rachel/utils/hardware.py

import torch
import platform

def detect_profile():
    """
    Detect optimal hardware profile for model inference.
    1. Cuda is preferred if available.
    2. Metal/MPS is used on Apple Silicon Macs.
    3. Fallback to CPU if neither is available.
    """
    if platform.system() == "Darwin" and platform.processor() == "arm":
        try:
            import mlx
            return "metal"
        except ImportError:
            pass
    
    if torch.cuda.is_available():
        return "cuda"
    
    return "cpu"


def resolve_device_and_type(device: str, compute_type: str) -> tuple[str, str]:
    """
    Resolves 'auto' values for device and compute_type, and prints status info.
    Handles platform-specific optimizations for all backends.
    """
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16" if compute_type == "auto" else compute_type
            print("✅ CUDA support")
        elif platform.system() == "Darwin" and platform.processor() == "arm":
            device = "mps"
            compute_type = "float32" if compute_type == "auto" else compute_type
            print("✅ Metal/MPS support detected")
        else:
            device = "cpu"
            compute_type = "int8" if compute_type == "auto" else compute_type
            print("✅ Using CPU... godspeed")

    if compute_type == "auto":
        compute_type = {
            "cuda": "float16",
            "cpu": "int8",
            "mps": "float32"
        }.get(device, "float32")

    print(f"✅ Resolved using: device={device}, compute_type={compute_type}")
    return device, compute_type