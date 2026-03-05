#!/usr/bin/env python3
"""
promote_ui.py — 非互動式 staging → PROD promote
在 menu-dashboard-staging container 內執行
"""
import os, sys, shutil, socket, struct, http.client, json
import subprocess, datetime

STAGING   = "/app"                                  # staging_dir 掛為 /app
PROD      = "/home/pi53/dashboard/current"         # 掛為 :rw
BACKUP    = "/home/pi53/dashboard/_prod_backup"    # 掛為 :rw
TG_ENV    = "/home/pi53/dashboard/.telegram_env"   # 掛為 :ro
LOG_FILE  = "/home/pi53/dashboard/logs/promote.log"
EXCLUDE   = ["data"]

# ── helpers ──────────────────────────────────────────────────

def ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    line = f"[{ts()}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def tg_notify(msg):
    if not os.path.exists(TG_ENV):
        return
    env = {}
    with open(TG_ENV) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                env[k] = v
    token   = env.get("TELEGRAM_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendMessage",
        "--data-urlencode", f"chat_id={chat_id}",
        "--data-urlencode", f"text={msg}",
        "-d", "parse_mode=HTML", "--max-time", "5",
    ], capture_output=True)

class _UnixConn(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect("/var/run/docker.sock")

def docker_restart(container):
    try:
        conn = _UnixConn("localhost")
        conn.request("POST", f"/containers/{container}/restart",
                     headers={"Content-Length": "0"})
        r = conn.getresponse()
        return r.status in (200, 204)
    except Exception as e:
        log(f"Docker restart error: {e}")
        return False

def _is_excluded(rel_path):
    rel_path = rel_path.replace("\\", "/")
    for pat in EXCLUDE:
        pat = pat.rstrip("/")
        if rel_path == pat or rel_path.startswith(pat + "/"):
            return True
    return False

def sync_dirs(src, dst):
    """src/ → dst/ 同步，含刪除，支援 exclude。"""
    src, dst = src.rstrip("/"), dst.rstrip("/")
    # 複製 / 更新
    for dirpath, dirnames, filenames in os.walk(src):
        rel_dir = os.path.relpath(dirpath, src)
        rel_dir = "" if rel_dir == "." else rel_dir
        if rel_dir and _is_excluded(rel_dir):
            dirnames.clear(); continue
        dirnames[:] = [d for d in dirnames
                       if not _is_excluded(os.path.join(rel_dir, d) if rel_dir else d)]
        for fname in filenames:
            rel_file = (os.path.join(rel_dir, fname) if rel_dir else fname).replace("\\", "/")
            if _is_excluded(rel_file):
                continue
            dst_file = os.path.join(dst, rel_file)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(os.path.join(dirpath, fname), dst_file)
    # 刪除 dst 中不存在於 src 的檔案
    for dirpath, dirnames, filenames in os.walk(dst):
        rel_dir = os.path.relpath(dirpath, dst)
        rel_dir = "" if rel_dir == "." else rel_dir
        if rel_dir and _is_excluded(rel_dir):
            dirnames.clear(); continue
        dirnames[:] = [d for d in dirnames
                       if not _is_excluded(os.path.join(rel_dir, d) if rel_dir else d)]
        for fname in filenames:
            rel_file = (os.path.join(rel_dir, fname) if rel_dir else fname).replace("\\", "/")
            if _is_excluded(rel_file):
                continue
            if not os.path.exists(os.path.join(src, rel_file)):
                os.remove(os.path.join(dirpath, fname))
    # 刪除 dst 中已空的目錄
    for dirpath, _, _ in os.walk(dst, topdown=False):
        rel = os.path.relpath(dirpath, dst)
        if rel in (".", "") or _is_excluded(rel.replace("\\", "/")):
            continue
        if not os.path.exists(os.path.join(src, rel)):
            try:
                os.rmdir(dirpath)
            except OSError:
                pass

# ── main ─────────────────────────────────────────────────────

deployed_txt = os.path.join(STAGING, "DEPLOYED.txt")
if not os.path.exists(deployed_txt):
    print("ERROR: DEPLOYED.txt not found — nothing to promote.")
    sys.exit(1)

with open(deployed_txt) as f:
    job = f.read().strip()

log(f"PROMOTE start: {job}")

# 1. 備份目前 PROD
log("Step 1/4: Backup PROD → _prod_backup ...")
os.makedirs(BACKUP, exist_ok=True)
try:
    sync_dirs(PROD, BACKUP)
    log("  backup OK")
except Exception as e:
    log(f"  WARNING: backup failed: {e}, continuing...")

# 2. Telegram 通知
tg_notify(f"🔄 <b>推送開始 → PROD</b>\nJob: <code>{job}</code>")

# 3. 同步 staging → PROD
log("Step 2/4: Sync staging → PROD ...")
try:
    sync_dirs(STAGING, PROD)
    log("  sync OK")
except Exception as e:
    log(f"ERROR: sync failed: {e}")
    sys.exit(1)

# 4. 重啟 PROD
log("Step 3/4: Restart menu-dashboard ...")
ok = docker_restart("menu-dashboard")
log("  restart OK" if ok else "  WARNING: restart may have failed")

log(f"Step 4/4: PROMOTE done: {job}")
tg_notify(f"✅ <b>PROD 已更新</b>\nJob: <code>{job}</code>\n網址: https://dashboard.tfooddata.com")
print(f"✅ Promoted: {job}")
