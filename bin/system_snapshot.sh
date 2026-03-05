#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/dashboard"
STAGING_DIR="$BASE/staging_dir"
PROD_DIR="$BASE/current"
PROD_DB="$PROD_DIR/data/menu.db"
COMPOSE_FILE="$HOME/raspi-system/docker-compose.yml"
OUT_DIR="$BASE/snapshots"

mkdir -p "$OUT_DIR"

TS="$(date +%Y%m%d_%H%M%S)"
OUT="$OUT_DIR/SYSTEM_SNAPSHOT_${TS}.txt"

{
echo "======================================"
echo "PI5 SYSTEM SNAPSHOT"
echo "Generated at: $(date)"
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
echo "======================================"
echo

echo "===== 1) STAGING PAGES ====="
if [ -d "$STAGING_DIR/dashboard/pages" ]; then
    ls -la "$STAGING_DIR/dashboard/pages"
else
    echo "[WARN] staging pages not found"
fi
echo

echo "===== 2) STAGING STRUCTURE (depth=2) ====="
if [ -d "$STAGING_DIR" ]; then
    cd "$STAGING_DIR"
    find . -maxdepth 2 -type f | sort
else
    echo "[WARN] staging dir missing"
fi
echo

echo "===== 3) PROD STRUCTURE (depth=2) ====="
if [ -d "$PROD_DIR" ]; then
    cd "$PROD_DIR"
    find . -maxdepth 2 -type f | sort
else
    echo "[WARN] prod dir missing"
fi
echo

echo "===== 4) DATABASE SCHEMA ====="
if command -v sqlite3 >/dev/null 2>&1 && [ -f "$PROD_DB" ]; then
    sqlite3 "$PROD_DB" ".schema"
else
    echo "[WARN] sqlite3 missing or DB not found"
fi
echo

echo "===== 5) DOCKER STATUS ====="
if command -v docker >/dev/null 2>&1; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"
else
    echo "[INFO] docker not available"
fi
echo

echo "===== 6) DOCKER COMPOSE (first 200 lines) ====="
if [ -f "$COMPOSE_FILE" ]; then
    head -n 200 "$COMPOSE_FILE"
else
    echo "[WARN] docker-compose.yml not found"
fi
echo

echo "===== 7) DISK USAGE ====="
df -h
echo

} > "$OUT"

echo "======================================"
echo "SNAPSHOT CREATED:"
echo "$OUT"
echo "======================================"
