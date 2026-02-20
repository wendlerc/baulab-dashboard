#!/bin/bash
# Expose the GPU dashboard via Cloudflare Tunnel (trycloudflare.com)
# Run this after starting the Flask app: uv run python -m src.main

set -e
CLOUDFLARED="${CLOUDFLARED:-$HOME/.local/bin/cloudflared}"
if [[ ! -x "$CLOUDFLARED" ]]; then
  CLOUDFLARED="cloudflared"
fi
exec "$CLOUDFLARED" tunnel --url http://localhost:5000
