"""Background collector that runs nvidia-smi on each node via SSH."""

import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .config import (
    NODES,
    NVIDIA_SMI_FORMAT,
    NVIDIA_SMI_QUERY,
    POLL_INTERVAL,
    SSH_IDENTITY_FILE,
    SSH_TIMEOUT,
    SSH_USER,
)
from .parser import GPUInfo, parse_nvidia_smi_output


@dataclass
class NodeStatus:
    """Status for a single node."""

    status: str  # "ok" | "error"
    gpus: list[dict] = field(default_factory=list)
    message: str | None = None


def _query_node(host: str) -> NodeStatus:
    """Run nvidia-smi on a single node via SSH via jump host."""
    cmd = [
        "ssh",
        "-l",
        SSH_USER,
        "-i",
        SSH_IDENTITY_FILE,
        "-o",
        "ConnectTimeout=10",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "BatchMode=yes",
        host,
        "nvidia-smi",
        f"--query-gpu={NVIDIA_SMI_QUERY}",
        f"--format={NVIDIA_SMI_FORMAT}",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SSH_TIMEOUT,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            return NodeStatus(status="error", message=stderr[:200] or "nvidia-smi failed")
        gpus = parse_nvidia_smi_output(result.stdout)
        return NodeStatus(
            status="ok",
            gpus=[
                {
                    "index": g.index,
                    "name": g.name,
                    "utilization": g.utilization,
                    "memory_used": g.memory_used_mb,
                    "memory_total": g.memory_total_mb,
                    "temperature": g.temperature_c,
                }
                for g in gpus
            ],
        )
    except subprocess.TimeoutExpired:
        return NodeStatus(status="error", message="Connection timeout")
    except Exception as e:
        return NodeStatus(status="error", message=str(e)[:200])


def _collect_all() -> dict:
    """Query all nodes in parallel using ThreadPoolExecutor."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    data: dict[str, NodeStatus] = {}
    with ThreadPoolExecutor(max_workers=min(20, len(NODES) * 2)) as ex:
        futures = {ex.submit(_query_node, node): node for node in NODES}
        for future in as_completed(futures):
            node = futures[future]
            try:
                data[node] = future.result()
            except Exception as e:
                data[node] = NodeStatus(status="error", message=str(e)[:200])
    return data


# Shared cache, updated by background thread
_cache: dict = {}
_cache_lock = threading.Lock()


def get_status() -> dict:
    """Return current cached status (safe to call from any thread)."""
    with _cache_lock:
        if _cache:
            return dict(_cache)
        return {"last_updated": None, "nodes": {}}


def _background_loop():
    """Run collection loop every POLL_INTERVAL seconds."""
    while True:
        time.sleep(POLL_INTERVAL)
        try:
            _update_cache()
        except Exception:
            pass  # Keep running


def _update_cache():
    """Run collection and update cache."""
    global _cache
    data = _collect_all()
    result = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "nodes": {
            node: {
                "status": ns.status,
                "gpus": ns.gpus,
                "message": ns.message,
            }
            for node, ns in data.items()
        },
    }
    with _cache_lock:
        _cache = result


def start_collector():
    """Run initial collection, then start background collector thread."""
    _update_cache()
    thread = threading.Thread(target=_background_loop, daemon=True)
    thread.start()
