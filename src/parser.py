"""Parse nvidia-smi CSV output."""

from dataclasses import dataclass


@dataclass
class GPUInfo:
    """Parsed GPU information."""

    index: int
    name: str
    utilization: int  # 0-100
    memory_used_mb: int
    memory_total_mb: int
    temperature_c: int


def parse_nvidia_smi_output(output: str) -> list[GPUInfo]:
    """
    Parse nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu
    --format=csv,noheader,nounits
    """
    gpus: list[GPUInfo] = []
    for line in output.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        try:
            idx = int(parts[0])
            name = parts[1]
            util = _parse_int(parts[2], 0)
            mem_used = _parse_int(parts[3], 0)
            mem_total = _parse_int(parts[4], 0)
            temp = _parse_int(parts[5], 0)
            gpus.append(
                GPUInfo(
                    index=idx,
                    name=name,
                    utilization=min(100, max(0, util)),
                    memory_used_mb=mem_used,
                    memory_total_mb=mem_total,
                    temperature_c=temp,
                )
            )
        except (ValueError, IndexError):
            continue
    return gpus


def _parse_int(s: str, default: int) -> int:
    """Parse integer, return default on failure."""
    s = s.strip()
    if not s or s == "[N/A]":
        return default
    try:
        return int(float(s))
    except ValueError:
        return default
