#!/usr/bin/env bash
set -euo pipefail
BASE="/home/pi53/dashboard"

if [ ! -e "$BASE/previous" ]; then
  echo "[ERR] previous not found, cannot rollback."
  exit 1
fi

PREV_REAL="$(readlink -f "$BASE/previous")"
if [ ! -f "$PREV_REAL/dashboard/dashboard.py" ]; then
  echo "[ERR] previous entrypoint missing: $PREV_REAL/dashboard/dashboard.py"
  exit 1
fi

ln -sfn "$PREV_REAL" "$BASE/current"
sudo systemctl restart menu-dashboard.service
echo "✅ Rolled back to: $PREV_REAL"
