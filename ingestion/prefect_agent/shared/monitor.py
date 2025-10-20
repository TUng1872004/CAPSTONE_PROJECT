import torch
import psutil
from typing import Optional, Dict


# ----------------- GPU MONITORING -----------------
def is_gpu_available() -> bool:
    return torch.cuda.is_available()


def get_gpu_name() -> str:
    if is_gpu_available():
        return torch.cuda.get_device_name(0)
    return "CPU"


def get_gpu_memory_info() -> Optional[Dict[str, float]]:
    """Return GPU memory stats in MB, or None if no GPU."""
    if not is_gpu_available():
        return None

    gpu_id = 0 
    total = torch.cuda.get_device_properties(gpu_id).total_memory
    allocated = torch.cuda.memory_allocated(gpu_id)
    reserved = torch.cuda.memory_reserved(gpu_id)
    free = total - reserved

    return {
        "total_mb": total / 1024**2,
        "allocated_mb": allocated / 1024**2,
        "reserved_mb": reserved / 1024**2,
        "free_mb": free / 1024**2,
    }


def get_gpu_utilization() -> float:
    """Return GPU memory utilization % (0–100)."""
    if not is_gpu_available():
        return 0.0
    mem = get_gpu_memory_info()
    return (mem["allocated_mb"] / mem["total_mb"]) * 100 if mem and mem["total_mb"] > 0 else 0.0


# ----------------- CPU MONITORING -----------------
def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=0.0)


def get_per_cpu_usage() -> list:
    return psutil.cpu_percent(interval=0.0, percpu=True)


# ----------------- RAM MONITORING -----------------
def get_ram_info() -> Dict[str, float]:
    """Return RAM usage in MB."""
    mem = psutil.virtual_memory()
    return {
        "total_mb": mem.total / 1024**2,
        "available_mb": mem.available / 1024**2,
        "used_mb": mem.used / 1024**2,
        "percent": mem.percent,
    }


# ----------------- COMBINED STATUS -----------------
def get_system_status() -> Dict:
    """Return combined system utilization snapshot."""
    return {
        "cpu_percent": get_cpu_usage(),
        "ram": get_ram_info(),
        "gpu": {
            "name": get_gpu_name(),
            "memory": get_gpu_memory_info(),
            "utilization": get_gpu_utilization(),
        },
    }
