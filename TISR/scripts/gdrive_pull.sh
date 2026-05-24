#!/bin/bash
# Pull large files from Google Drive (gdrive-dcu remote)
# Usage: bash scripts/gdrive_pull.sh [models|dataset|all]
#   models  - pull only model checkpoints
#   dataset - pull only dataset
#   all     - pull everything (default)

REMOTE="gdrive-dcu:TISR"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-all}"

pull_models() {
  echo "=== Pulling models from GDrive ==="
  rclone copy "$REMOTE/experiments" "$REPO_ROOT/experiments" \
    --include "*.pth" --include "*.state" \
    --progress
}

pull_dataset() {
  echo "=== Pulling dataset from GDrive ==="
  mkdir -p /home/jovyan/work/data/CIDIS
  rclone copy "$REMOTE/data/CIDIS" /home/jovyan/work/data/CIDIS \
    --progress
}

case "$MODE" in
  models)  pull_models ;;
  dataset) pull_dataset ;;
  all)     pull_models; pull_dataset ;;
  *)       echo "Usage: $0 [models|dataset|all]"; exit 1 ;;
esac

echo "=== Done ==="
