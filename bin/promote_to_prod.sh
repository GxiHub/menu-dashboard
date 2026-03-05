#!/usr/bin/env bash
set -euo pipefail

BASE="/home/pi53/dashboard"

if [ ! -L "$BASE/staging" ]; then
  echo "[ERR] staging symlink not found: $BASE/staging"
  exit 1
fi

STAGING_REAL="$(readlink -f "$BASE/staging")"
if [ ! -f "$STAGING_REAL/dashboard/dashboard.py" ]; then
  echo "[ERR] staging entrypoint missing: $STAGING_REAL/dashboard/dashboard.py"
  exit 1
fi

# compile check (avoid broken python file)
python3 -m py_compile "$STAGING_REAL/dashboard/dashboard.py"

# move current -> previous, staging -> current
if [ -e "$BASE/current" ]; then
  ln -sfn "$(readlink -f "$BASE/current")" "$BASE/previous" || true
fi
ln -sfn "$STAGING_REAL" "$BASE/current"

# restart prod
sudo systemctl restart menu-dashboard.service
echo "✅ Promoted to production: $STAGING_REAL"
