# GPU Dashboard

A web dashboard that summarizes GPU utilization across SSH-accessible nodes by running `nvidia-smi` on each host.

## Setup

### 1. Requirements

- The machine running the dashboard must be able to SSH directly to each node
- `~/.ssh/id_ed25519_hakone` must exist (or edit `src/config.py` to change `SSH_IDENTITY_FILE`)
- SSH options (User, IdentityFile) are passed explicitly; `~/.ssh/config` is optional

### 2. Install and run

```bash
cd baulab-dashboard  # or clone from git@github.com:wendlerc/baulab-dashboard.git
uv sync
uv run python -m src.main
```

Open http://localhost:5000

### 3. Expose via Cloudflare Tunnel (optional)

To access from outside your network:

```bash
# Terminal 1: start the dashboard
uv run python -m src.main

# Terminal 2: start the tunnel
./run-tunnel.sh
```

The tunnel prints a URL like `https://random-name.trycloudflare.com` — open it in a browser. No Cloudflare account required.

## How it works

- A background thread runs `nvidia-smi` on each node every 60 seconds via SSH
- The web UI polls `/api/status` every 30 seconds
- Nodes are queried in parallel; connection timeout is 15 seconds per node
