#!/usr/bin/env bash

set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"
LOG_FILE="${LOG_FILE:-scan_results.log}"

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <image1> <image2> <image3>"
  exit 1
fi

: > "$LOG_FILE"

echo "Testing live backend at ${API_URL}" | tee -a "$LOG_FILE"
echo "Started at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

echo "== /test-connection ==" | tee -a "$LOG_FILE"
curl --silent --show-error "${API_URL}/test-connection" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

for image_path in "$@"; do
  if [ ! -f "$image_path" ]; then
    echo "Missing image file: $image_path" | tee -a "$LOG_FILE"
    exit 1
  fi

  echo "== /analyze :: ${image_path} ==" | tee -a "$LOG_FILE"
  curl --silent --show-error \
    -X POST "${API_URL}/analyze" \
    -F "file=@${image_path}" | tee -a "$LOG_FILE"
  echo | tee -a "$LOG_FILE"
  echo | tee -a "$LOG_FILE"
done

echo "Finished at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" | tee -a "$LOG_FILE"
