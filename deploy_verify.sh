#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-}"
JOB_ID="${2:-}"

[ -n "$ZIP_PATH" ] || { echo "Usage: $0 /path/to/upload.zip job_id"; exit 2; }
[ -n "$JOB_ID" ] || { echo "Usage: $0 /path/to/upload.zip job_id"; exit 2; }
[ -f "$ZIP_PATH" ] || { echo "ZIP not found: $ZIP_PATH"; exit 2; }

BASE="/home/pi53/dashboard"
JOBS_DIR="$BASE/incoming/jobs"
JOB_DIR="$JOBS_DIR/$JOB_ID"
LOG_DIR="$JOB_DIR/logs"
STATUS_JSON="$JOB_DIR/status.json"
DIFF_TXT="$JOB_DIR/diff.txt"

STAGING_DIR="$BASE/staging_dir"
WORK_DIR="$BASE/_work/$JOB_ID"
TMP_DIR="/tmp/dashboard_unzip/$JOB_ID"

mkdir -p "$JOB_DIR" "$LOG_DIR" "$WORK_DIR" "$TMP_DIR"

json_escape() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e ':a;N;$!ba;s/\n/\\n/g'; }
write_status() {
  local state="$1" level="$2" msg="$3"
  local msg_esc; msg_esc="$(json_escape "$msg")"
  cat > "$STATUS_JSON" <<JSON
{"job_id":"$JOB_ID","updated_at":"$(date -Iseconds)","state":"$state","level":"$level","message":"$msg_esc",
 "paths":{"job_dir":"$JOB_DIR","zip":"$ZIP_PATH","work_dir":"$WORK_DIR","staging_dir":"$STAGING_DIR","tmp_dir":"$TMP_DIR"}}
JSON
}

step() {
  local key="$1" name="$2"; shift 2
  local log="$LOG_DIR/${key}.log"
  echo "== $key: $name ==" | tee "$log"
  { "$@"; } >>"$log" 2>&1
}

fail() { write_status "FAILED" "FAIL" "$1"; echo "FAILED: $1"; exit 10; }

write_status "RUNNING" "INFO" "verify start"

step 01_zip "zip integrity" bash -lc "unzip -t '$ZIP_PATH' >/dev/null" || fail "zip integrity failed"
step 02_zipslip "zip slip" bash -lc "if unzip -Z1 '$ZIP_PATH' | grep -E '(^/|^\.\./|/\.\./)' >/dev/null; then exit 1; fi" || fail "zip slip detected"

step 03_unzip "unzip" bash -lc "
rm -rf '$TMP_DIR' && mkdir -p '$TMP_DIR'
unzip -q '$ZIP_PATH' -d '$TMP_DIR'
root='$TMP_DIR'
if [ -z \"\$(find '$TMP_DIR' -mindepth 1 -maxdepth 1 -type f -print -quit)\" ]; then
  dcount=\"\$(find '$TMP_DIR' -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')\"
  [ \"\$dcount\" = \"1\" ] && root=\"\$(find '$TMP_DIR' -mindepth 1 -maxdepth 1 -type d -print -quit)\"
fi
echo \"ROOT=\$root\" > '$WORK_DIR/.root_path'
" || fail "unzip failed"

root="$(sed -n 's/^ROOT=//p' "$WORK_DIR/.root_path" | tail -n 1)"
[ -n "$root" ] || fail "root not found"
[ -f "$root/dashboard/dashboard.py" ] || fail "missing dashboard/dashboard.py"

step 04_snapshot "snapshot to work" bash -lc "rm -rf '$WORK_DIR' && mkdir -p '$WORK_DIR' && rsync -a --delete '$root/.' '$WORK_DIR/.'" || fail "snapshot failed"

step 05_diff "diff vs staging" bash -lc "rsync -ani --delete '$WORK_DIR/.' '$STAGING_DIR/.' | sed -n '1,400p' | tee '$DIFF_TXT'" || true

step 06_pycompile "py_compile" bash -lc "
cd '$WORK_DIR'
python3 - <<'PY'
import os, sys, py_compile
bad=[]
for r,_,fs in os.walk('.'):
  for f in fs:
    if f.endswith('.py'):
      p=os.path.join(r,f)
      try: py_compile.compile(p, doraise=True)
      except Exception as e: bad.append((p,str(e)))
if bad:
  print('PY_COMPILE_FAIL')
  for p,e in bad[:50]: print(p,e)
  sys.exit(1)
print('PY_COMPILE_OK')
PY
" || fail "py_compile failed"


write_status "READY" "OK" "verified ok (not deployed)"
echo "READY: $JOB_ID"
