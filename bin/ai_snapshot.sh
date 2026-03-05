#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/dashboard"
STAGING_DIR="$BASE/staging_dir"
PROD_DB="$BASE/current/data/menu.db"
OUT_DIR="$BASE/snapshots"
mkdir -p "$OUT_DIR"

TS="$(date +%Y%m%d_%H%M%S)"
OUT="$OUT_DIR/PROJECT_SNAPSHOT_${TS}.txt"

{
  echo "=============================="
  echo "Pi5 PROJECT SNAPSHOT"
  echo "Generated at: $(date)"
  echo "Host: $(hostname)"
  echo "User: $(whoami)"
  echo "=============================="
  echo

  echo "===== A) PAGES LIST ====="
  if [ -d "$STAGING_DIR/dashboard/pages" ]; then
    ls -la "$STAGING_DIR/dashboard/pages"
  else
    echo "[WARN] missing: $STAGING_DIR/dashboard/pages"
  fi
  echo

  echo "===== B) PROJECT STRUCTURE (maxdepth=2) ====="
  if [ -d "$STAGING_DIR" ]; then
    ( cd "$STAGING_DIR" && find . -maxdepth 2 -type f | sort )
  else
    echo "[WARN] missing: $STAGING_DIR"
  fi
  echo

  echo "===== C) DATABASE SCHEMA ====="
  if command -v sqlite3 >/dev/null 2>&1; then
    if [ -f "$PROD_DB" ]; then
      sqlite3 "$PROD_DB" ".schema"
    else
      echo "[WARN] missing DB: $PROD_DB"
    fi
  else
    echo "[WARN] sqlite3 not installed"
  fi
  echo

  echo "===== D) DOCKER CONTAINERS (optional) ====="
  if command -v docker >/dev/null 2>&1; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}" || true
  else
    echo "[INFO] docker not found"
  fi
  echo

} > "$OUT"

echo "================================="
echo "SNAPSHOT CREATED:"
echo "$OUT"
echo "================================="
