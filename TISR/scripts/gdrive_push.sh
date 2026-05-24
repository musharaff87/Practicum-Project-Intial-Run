#!/bin/bash
# Push large files to Google Drive (gdrive-dcu remote)
# Usage: bash scripts/gdrive_push.sh

REMOTE="gdrive-dcu:TISR"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Pushing models to GDrive ==="
rclone copy "$REPO_ROOT/experiments" "$REMOTE/experiments" \
  --include "*.pth" --include "*.state" \
  --progress

echo "=== Pushing pretrained models ==="
rclone copy "$REPO_ROOT/experiments/pretrained_models" "$REMOTE/experiments/pretrained_models" \
  --progress

echo "=== Pushing dataset ==="
rclone copy /home/jovyan/work/data/CIDIS "$REMOTE/data/CIDIS" \
  --progress

echo "=== Done. Files are at gdrive-dcu:TISR ==="
