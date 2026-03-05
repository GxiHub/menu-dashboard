#!/usr/bin/env bash
# watchdog.sh - 每 5 分鐘檢查關鍵服務，異常/恢復時發 Telegram 通知

set -uo pipefail

BASE="/home/pi53/dashboard"
TELEGRAM_ENV="$BASE/.telegram_env"
ALERT_DIR="$BASE/logs/watchdog_alerts"

mkdir -p "$ALERT_DIR"

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

# 冷卻機制：同一服務 60 分鐘內只發一次警報
should_alert() {
  local key="$1"
  local cooldown="${2:-3600}"
  local flag="$ALERT_DIR/${key}.flag"
  local now
  now=$(date +%s)
  if [ -f "$flag" ]; then
    local last
    last=$(cat "$flag")
    local diff=$(( now - last ))
    [ "$diff" -lt "$cooldown" ] && return 1
  fi
  echo "$now" > "$flag"
  return 0
}

# 恢復通知：服務從異常恢復正常時發送
clear_alert() {
  local key="$1"
  local flag="$ALERT_DIR/${key}.flag"
  if [ -f "$flag" ]; then
    rm -f "$flag"
    return 0  # 之前有警報，現已恢復
  fi
  return 1  # 之前就正常，不需通知
}

check_http() {
  local name="$1"
  local url="$2"
  local key="$3"
  if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
    if clear_alert "$key"; then
      echo "[$(date '+%F %T')] RECOVER $name"
      tg_notify "✅ <b>服務已恢復</b>: $name"
    else
      echo "[$(date '+%F %T')] OK      $name"
    fi
  else
    echo "[$(date '+%F %T')] FAIL    $name ($url)"
    if should_alert "$key"; then
      tg_notify "🚨 <b>服務異常</b>: $name&#10;時間: $(date '+%Y-%m-%d %H:%M')"
    fi
  fi
}

check_docker() {
  local name="$1"
  local key="docker_${name}"
  if docker ps --filter "name=^${name}$" --filter "status=running" \
       --format "{{.Names}}" 2>/dev/null | grep -q "^${name}$"; then
    if clear_alert "$key"; then
      echo "[$(date '+%F %T')] RECOVER 容器 $name"
      tg_notify "✅ <b>容器已恢復</b>: $name"
    else
      echo "[$(date '+%F %T')] OK      容器 $name"
    fi
  else
    echo "[$(date '+%F %T')] FAIL    容器 $name"
    if should_alert "$key"; then
      tg_notify "🚨 <b>容器異常</b>: $name&#10;時間: $(date '+%Y-%m-%d %H:%M')"
    fi
  fi
}

# ── 執行檢查 ──────────────────────────────────────────────────
check_http   "PROD"     "http://127.0.0.1:8501" "prod_http"
check_http   "Staging"  "http://127.0.0.1:8502" "staging_http"
check_http   "PiUpload" "http://127.0.0.1:8052" "piupload_http"
check_docker "menu-dashboard"
check_docker "zip-deploy-watcher"
