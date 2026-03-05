#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-}"
JOB_ID="${2:-}"

[ -n "$ZIP_PATH" ] || { echo "Usage: $0 /path/to/upload.zip [job_id]"; exit 2; }
[ -f "$ZIP_PATH" ] || { echo "ZIP not found: $ZIP_PATH"; exit 2; }

JOB_DIR="$(cd "$(dirname "$ZIP_PATH")" && pwd)"
JOBS_DIR="$(cd "$(dirname "$JOB_DIR")" && pwd)"
LOG_DIR="$JOB_DIR/logs"
STATUS_JSON="$JOB_DIR/status.json"

BASE="/home/pi53/dashboard"
STAGING_DIR="$BASE/staging_dir"
WORK_BASE="$BASE/_work"
TMP_BASE="/tmp/dashboard_unzip"

ts="$(date +%Y%m%d_%H%M%S)"
job_id="${JOB_ID:-$ts}"

work="$WORK_BASE/$job_id"
tmp="$TMP_BASE/$job_id"

mkdir -p "$LOG_DIR" "$STAGING_DIR" "$WORK_BASE" "$TMP_BASE" "$work" "$tmp"

command -v unzip >/dev/null 2>&1 || { echo "unzip not installed"; exit 3; }
command -v rsync >/dev/null 2>&1 || { echo "rsync not installed"; exit 3; }

# 每個檔案 diff 最多顯示幾行
DIFF_MAX_LINES=50

# 這些副檔名才做內容 diff（文字檔）
is_text_file() {
  local f="$1"
  case "${f##*.}" in
    py|sh|md|toml|txt|csv|yml|yaml|json|cfg|ini|html|js|css|ts) return 0 ;;
    *) return 1 ;;
  esac
}

# ── log helpers ─────────────────────────────────────────────
_stage_start=0
log() {
  local stage="$1"; shift
  echo "[$(date '+%F %T')] [$stage] $*"
}
stage() {
  _stage_start=$(date +%s%N)
  log "STAGE" "▶ $*"
}
stage_ok() {
  local elapsed_ms=$(( ($(date +%s%N) - _stage_start) / 1000000 ))
  log "STAGE" "✓ $* (${elapsed_ms}ms)"
}
stage_fail() {
  log "STAGE" "✗ FAILED: $*"
}

# ── status.json helper ──────────────────────────────────────
json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e ':a;N;$!ba;s/\n/\\n/g'
}
write_status() {
  local state="$1" level="$2" msg="$3"
  local msg_esc
  msg_esc="$(json_escape "$msg")"
  cat > "$STATUS_JSON" <<JSON
{
  "job_id": "$(printf '%s' "$job_id")",
  "updated_at": "$(date -Iseconds)",
  "state": "$(printf '%s' "$state")",
  "level": "$(printf '%s' "$level")",
  "message": "$msg_esc",
  "paths": {
    "job_dir": "$(printf '%s' "$JOB_DIR")",
    "zip": "$(printf '%s' "$ZIP_PATH")",
    "staging_dir": "$(printf '%s' "$STAGING_DIR")",
    "work_dir": "$(printf '%s' "$work")"
  },
  "logs": {
    "deploy": "logs/deploy.log"
  }
}
JSON
}

# ── Telegram notification ─────────────────────────────────────
TELEGRAM_ENV="$BASE/.telegram_env"
tg_notify() {
  local msg="$1"
  [ -f "$TELEGRAM_ENV" ] || return 0
  local TELEGRAM_TOKEN="" TELEGRAM_CHAT_ID=""
  # shellcheck disable=SC1090
  source "$TELEGRAM_ENV"
  [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ] || return 0
  local encoded_msg
  encoded_msg="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$msg" 2>/dev/null || echo "$msg")"
  wget -q -O /dev/null --timeout=5 \
    --post-data "chat_id=${TELEGRAM_CHAT_ID}&text=${encoded_msg}&parse_mode=HTML" \
    "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" 2>/dev/null || true
}

# ════════════════════════════════════════════════════════════
log "JOB"   "job_id  : $job_id"
log "JOB"   "zip     : $ZIP_PATH  ($(du -sh "$ZIP_PATH" | cut -f1))"
log "JOB"   "staging : $STAGING_DIR"
echo ""
write_status "DEPLOYING" "INFO" "starting deploy"
tg_notify "🚀 <b>部署開始</b>\nJob: <code>$job_id</code>\n檔案: $(basename \"$ZIP_PATH\")"

# ── Stage 1: zip integrity ───────────────────────────────────
stage "zip integrity check"
if ! unzip -t "$ZIP_PATH" >/dev/null 2>&1; then
  stage_fail "zip integrity check"
  write_status "FAILED" "FAIL" "zip file corrupted"
  tg_notify "❌ <b>部署失敗</b>\nJob: <code>$job_id</code>\n原因: zip 損壞"
  exit 4
fi
stage_ok "zip integrity check"

# ── Stage 2: zip slip check ──────────────────────────────────
stage "zip slip security check"
if unzip -Z1 "$ZIP_PATH" | grep -E '(^/|^\.\./|/\.\./)' >/dev/null 2>&1; then
  stage_fail "zip slip security check"
  write_status "FAILED" "FAIL" "zip slip detected"
  tg_notify "❌ <b>部署失敗</b>\nJob: <code>$job_id</code>\n原因: zip slip 安全檢查失敗"
  exit 4
fi
stage_ok "zip slip security check"

# ── Stage 3: zip contents listing ───────────────────────────
stage "zip contents"
zip_size="$(du -sh "$ZIP_PATH" | cut -f1)"
file_count="$(unzip -Z1 "$ZIP_PATH" | wc -l | tr -d ' ')"
log "ZIP" "壓縮檔大小：$zip_size，共 $file_count 個項目"
log "ZIP" "── 內容清單 ──────────────────────────────"
unzip -Z "$ZIP_PATH" | awk 'NR>1 && /^[-dl]/ {
  size=$4; date=$7; time=$8; name=$9
  printf "  %-10s  %-12s  %s %s  %s\n", $1, size, date, time, name
}'
log "ZIP" "──────────────────────────────────────────"
stage_ok "zip contents"

# ── Stage 4: unzip ──────────────────────────────────────────
stage "unzip to temp"
rm -rf "$tmp"
mkdir -p "$tmp"
unzip -q "$ZIP_PATH" -d "$tmp"

root="$tmp"
if [ -z "$(find "$tmp" -mindepth 1 -maxdepth 1 -type f -print -quit)" ]; then
  dcount="$(find "$tmp" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  if [ "$dcount" = "1" ]; then
    root="$(find "$tmp" -mindepth 1 -maxdepth 1 -type d -print -quit)"
    log "UNZIP" "偵測到單一根目錄：$(basename "$root")，自動進入"
  fi
fi
stage_ok "unzip to temp"

# ── Stage 5: structure check ─────────────────────────────────
stage "package structure check"
if [ ! -d "$root/dashboard" ] || [ ! -f "$root/dashboard/dashboard.py" ]; then
  stage_fail "package structure check"
  log "ERR" "缺少 dashboard/dashboard.py，以下為解壓內容："
  ls -la "$root" | sed -n "1,30p"
  write_status "FAILED" "FAIL" "missing dashboard/dashboard.py"
  tg_notify "❌ <b>部署失敗</b>\nJob: <code>$job_id</code>\n原因: 缺少 dashboard/dashboard.py"
  exit 5
fi
log "STRUCT" "結構驗證通過：dashboard/dashboard.py 存在"
stage_ok "package structure check"

# ── Stage 6: diff vs current staging ────────────────────────
stage "diff vs staging"
if [ -d "$STAGING_DIR" ] && [ "$(ls -A "$STAGING_DIR" 2>/dev/null)" ]; then
  new_files=0; mod_files=0; del_files=0
  mod_list=()

  log "DIFF" "── 檔案異動清單 ────────────────────────────"
  while IFS= read -r line; do
    flag="${line:0:1}"
    fname="${line:12}"
    [ -z "$fname" ] && continue
    # 跳過目錄行
    [[ "$fname" == */ ]] && continue
    case "$flag" in
      ">"|"<")
        if echo "$line" | grep -q "^>f+++++"; then
          log "DIFF" "  [新增] $fname"
          new_files=$((new_files+1))
        else
          log "DIFF" "  [更新] $fname"
          mod_files=$((mod_files+1))
          mod_list+=("$fname")
        fi
        ;;
      "*")
        log "DIFF" "  [刪除] $fname"
        del_files=$((del_files+1))
        ;;
    esac
  done < <(rsync -a --delete --dry-run --itemize-changes "$root/." "$STAGING_DIR/." 2>/dev/null || true)

  log "DIFF" "──────────────────────────────────────────"
  log "DIFF" "彙總：新增 $new_files 個 | 更新 $mod_files 個 | 刪除 $del_files 個"

  # ── Stage 6b: content diff for modified text files ────────
  if [ "${#mod_list[@]}" -gt 0 ]; then
    echo ""
    log "DIFF" "── 內容變更（文字檔，每檔最多 ${DIFF_MAX_LINES} 行）──"
    for fname in "${mod_list[@]}"; do
      if ! is_text_file "$fname"; then
        log "DIFF" "  [$fname] → 二進位檔，跳過內容比對"
        continue
      fi
      old_f="$STAGING_DIR/$fname"
      new_f="$root/$fname"
      [ -f "$old_f" ] || continue
      [ -f "$new_f" ] || continue

      diff_out="$(diff --unified=2 "$old_f" "$new_f" 2>/dev/null || true)"
      if [ -z "$diff_out" ]; then
        # rsync 說有改（時間戳），但內容相同
        log "DIFF" "  [$fname] → 內容無變化（僅時間戳不同）"
        continue
      fi

      total_lines="$(echo "$diff_out" | wc -l)"
      log "DIFF" "  ┌─ $fname（共 $total_lines 行差異）"
      echo "$diff_out" | head -n "$DIFF_MAX_LINES" | while IFS= read -r dline; do
        log "DIFF" "  │ $dline"
      done
      if [ "$total_lines" -gt "$DIFF_MAX_LINES" ]; then
        log "DIFF" "  │ ... （省略 $((total_lines - DIFF_MAX_LINES)) 行，完整 diff 請見 deploy.log）"
      fi
      log "DIFF" "  └─"
    done
    log "DIFF" "──────────────────────────────────────────"
  fi
else
  log "DIFF" "staging 為空，視為全新部署"
fi
stage_ok "diff vs staging"

# ── Stage 7: rsync to work ───────────────────────────────────
stage "rsync to work dir (clean snapshot)"
rsync -a --delete --exclude="data/menu.db" --exclude="data/backup/" "$root/." "$work/."
stage_ok "rsync to work dir"

# ── Stage 8: rsync to staging ────────────────────────────────
stage "rsync to staging_dir"
rsync -a --delete --exclude="data/menu.db" --exclude="data/backup/" "$work/." "$STAGING_DIR/."
echo "$job_id" > "$STAGING_DIR/DEPLOYED.txt"
stage_ok "rsync to staging_dir"

# ── Stage 9: regenerate PROJECT.md ───────────────────────────
PROJ_SCRIPT="$HOME/generate_project_md.sh"
if [ -x "$PROJ_SCRIPT" ]; then
  stage "regenerate PROJECT.md"
  bash "$PROJ_SCRIPT" >/dev/null 2>&1 && stage_ok "regenerate PROJECT.md" \
    || log "WARN" "PROJECT.md 產生失敗（不影響部署）"
fi

# ════════════════════════════════════════════════════════════
echo ""
write_status "DEPLOYED" "OK" "deployed to staging_dir"
tg_notify "✅ <b>部署成功 → Staging</b>\nJob: <code>$job_id</code>\n檔案: $(basename \"$ZIP_PATH\")"
log "DONE" "✅ 部署完成 → $STAGING_DIR"
log "DONE" "DEPLOYED: $job_id"
