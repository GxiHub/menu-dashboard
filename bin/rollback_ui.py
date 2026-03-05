#!/usr/bin/env python3
"""
rollback_ui.py — PROD 回滾到上一次 promote 前的備份
在 menu-dashboard-staging container 內執行
"""
import os, sys, shutil, socket, http.client
import subprocess, datetime

PROD      = "/home/pi53/dashboard/current"
BACKUP    = "/home/pi53/dashboard/_prod_backup"
TG_ENV    = "/home/pi53/dashboard/.telegram_env"
LOG_FILE  = "/home/pi53/dashboard/logs/promote.log"
EXCLUDE   = ["data/menu.db", "data/backup"]

# ── helpers（與 promote_ui.py 相同）────────────────────────────

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
    src, dst = src.rstrip("/"), dst.rstrip("/")
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

if not os.path.isdir(BACKUP) or not os.listdir(BACKUP):
    print("ERROR: 沒有備份可以回滾。請先執行一次 Promote 建立備份。")
    sys.exit(1)

backup_ver = "(unknown)"
ver_file = os.path.join(BACKUP, "VERSION.txt")
if os.path.exists(ver_file):
    with open(ver_file) as f:
        backup_ver = f.read().strip()

log(f"ROLLBACK start: target = {backup_ver}")
tg_notify(f"↩️ <b>PROD 回滾中</b>\n目標版本: <code>{backup_ver}</code>")

log("Step 1/2: Sync _prod_backup → PROD ...")
try:
    sync_dirs(BACKUP, PROD)
    log("  sync OK")
except Exception as e:
    log(f"ERROR: sync failed: {e}")
    sys.exit(1)

log("Step 2/2: Restart menu-dashboard ...")
ok = docker_restart("menu-dashboard")
log("  restart OK" if ok else "  WARNING: restart may have failed")

log(f"ROLLBACK done: {backup_ver}")
tg_notify(f"✅ <b>PROD 已回滾</b>\n版本: <code>{backup_ver}</code>")
print(f"✅ Rollback done: {backup_ver}")
