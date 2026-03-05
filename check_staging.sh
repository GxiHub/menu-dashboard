#!/usr/bin/env bash
set -euo pipefail

STG=/home/pi53/dashboard/staging_dir
C=menu-dashboard-staging

echo "== time =="
date
docker exec zip-deploy-watcher date || true
docker exec "$C" date || true

echo
echo "== host DEPLOYED.txt =="
cat "$STG/DEPLOYED.txt" 2>/dev/null || echo "NO DEPLOYED.txt"

echo
echo "== container DEPLOYED.txt =="
docker exec "$C" sh -lc 'cat /app/DEPLOYED.txt 2>/dev/null || echo "NO /app/DEPLOYED.txt"'

echo
echo "== key file mtimes (host vs container) =="
TZ=Asia/Taipei stat -c "HOST  mtime=%y size=%s %n" "$STG/dashboard/dashboard.py" "$STG/dashboard/admin_panels.py" 2>/dev/null || true
docker exec "$C" sh -lc 'TZ=Asia/Taipei stat -c "CTNR  mtime=%y size=%s %n" /app/dashboard/dashboard.py /app/dashboard/admin_panels.py 2>/dev/null || true'

echo
echo "== http 8502 =="
curl -sS -I http://127.0.0.1:8502 | head -n 10 || true
