"""Configuration for GPU dashboard."""

import os

# Nodes to query
NODES = [
    "kawasaki",
    "kumamoto",
    "macondo",
    "hokkaido",
    "andromeda",
    "sendai",
    "naoshima",
    "karasuno",
    "karakuri",
    "hawaii",
    "tokyo",
    "umibozu",
    "kyoto",
    "saitama",
    "bippu",
    "osaka",
    "hamada",
    "hakone",
]

# nvidia-smi query format for parsing
NVIDIA_SMI_QUERY = (
    "index,name,utilization.gpu,memory.used,memory.total,temperature.gpu"
)
NVIDIA_SMI_FORMAT = "csv,noheader,nounits"

# Poll interval in seconds
POLL_INTERVAL = 60

# SSH timeout per node in seconds
SSH_TIMEOUT = 15

# SSH connection options (passed explicitly so config is not required)
SSH_USER = "wendler"
SSH_IDENTITY_FILE = os.path.expanduser("~/.ssh/id_ed25519_hakone")
