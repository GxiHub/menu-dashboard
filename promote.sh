#!/usr/bin/env bash
set -euo pipefail

BASE="/home/pi53/dashboard"
STAGING="$BASE/staging_dir"
PROD="$BASE/current"
LOG="$BASE/logs/promote.log"

mkdir -p "$BASE/logs"
# ── Telegram notification ─────────────────────────────────────
TELEGRAM_ENV="$(dirname "$0")/.telegram_env"
tg_notify() {
  local msg="$1"
  [ -f "$TELEGRAM_ENV" ] || return 0
  local TELEGRAM_TOKEN="" TELEGRAM_CHAT_ID=""
  source "$TELEGRAM_ENV"
  [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ] || return 0
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${msg}" \
    -d "parse_mode=HTML" \
    --max-time 5 >/dev/null 2>&1 || true
}

echo "=== PROMOTE CHECK ==="

if [ ! -f "$STAGING/DEPLOYED.txt" ]; then
  echo "ERROR: no DEPLOYED.txt in staging — nothing to promote."
  exit 1
fi

JOB=$(cat "$STAGING/DEPLOYED.txt")
echo "Staging job : $JOB"
echo ""

echo "=== Files that will change in PROD ==="
rsync -ani --delete   --exclude='data/menu.db'   --exclude='data/backup/'   "$STAGING/." "$PROD/." | grep -v '^\./$' | head -40 || true
echo ""

read -rp "Promote to PROD? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

tg_notify "🔄 <b>推送開始 → PROD</b>\nJob: <code>$JOB</code>"
echo "[$(date -Iseconds)] PROMOTE start: $JOB" | tee -a "$LOG"

rsync -a --delete   --exclude='data/menu.db'   --exclude='data/backup/'   "$STAGING/." "$PROD/."

docker restart menu-dashboard

echo "[$(date -Iseconds)] PROMOTE done: $JOB" | tee -a "$LOG"
tg_notify "✅ <b>PROD 已更新</b>\nJob: <code>$JOB</code>\n網址: https://dashboard.tfooddata.com"
echo ""
echo "PROD is now running: $JOB"
echo "Check: https://dashboard.tfooddata.com"
