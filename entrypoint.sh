#!/bin/bash
# Cloud Run entrypoint script
# Reads PORT environment variable (set by Cloud Run) and starts uvicorn

set -e

# Get PORT from environment, default to 8080
PORT="${PORT:-8080}"
HOST="0.0.0.0"

# Log startup info
echo "Starting NutriScan AI API"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Python version: $(python --version)"
echo "---"

# Use exec to replace the shell process with uvicorn
# This ensures proper signal handling for Cloud Run graceful shutdown
exec uvicorn backend.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --log-level info
