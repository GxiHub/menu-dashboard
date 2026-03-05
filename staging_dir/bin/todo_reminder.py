#!/usr/bin/env python3
"""Todo reminder — safe to run every minute (idempotent via reminded_at).

Usage:
    python bin/todo_reminder.py
    # or via docker:
    docker exec menu-dashboard python /app/bin/todo_reminder.py
"""
from __future__ import annotations

import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent   # .../current/bin  or .../staging_dir/bin
BASE_DIR   = SCRIPT_DIR.parent                 # .../current      or .../staging_dir
DB_PATH    = BASE_DIR / "data" / "menu.db"
TG_ENV     = BASE_DIR.parent / ".telegram_env" # ~/dashboard/.telegram_env

# ── schema init ───────────────────────────────────────────────────────────────

_INIT_SQL = """
CREATE TABLE IF NOT EXISTS todo_items (
    id          INTEGER PRIMARY KEY,
    title       TEXT    NOT NULL,
    description TEXT    DEFAULT "",
    status      TEXT    NOT NULL DEFAULT "open",
    priority    INTEGER NOT NULL DEFAULT 2,
    owner_user  TEXT    NOT NULL,
    created_by  TEXT    NOT NULL,
    updated_by  TEXT    NOT NULL,
    deleted_by  TEXT,
    deadline_at TEXT,
    remind_at   TEXT,
    reminded_at TEXT,
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL,
    deleted_at  TEXT
);
CREATE TABLE IF NOT EXISTS todo_activity_log (
    id          INTEGER PRIMARY KEY,
    todo_id     INTEGER,
    action      TEXT    NOT NULL,
    actor_user  TEXT    NOT NULL,
    before_json TEXT,
    after_json  TEXT,
    created_at  TEXT    NOT NULL
);
"""

# ── Telegram ──────────────────────────────────────────────────────────────────

def _load_tg() -> tuple[str, str]:
    token = chat_id = ""
    for p in [TG_ENV, Path("/run/secrets/telegram_env")]:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k == "TELEGRAM_TOKEN":
                        token = v
                    elif k == "TELEGRAM_CHAT_ID":
                        chat_id = v
            break
    return token, chat_id

def _send_tg(token: str, chat_id: str, text: str) -> bool:
    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    ).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"[WARN] Telegram HTTP error: {e}")
        return False

# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not DB_PATH.exists():
        print(f"[INFO] DB not found: {DB_PATH}")
        return

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    token, chat_id = _load_tg()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(_INIT_SQL)

        rows = conn.execute(
            """
            SELECT id, title, owner_user, deadline_at, status
            FROM todo_items
            WHERE remind_at <= ?
              AND reminded_at IS NULL
              AND status      != "done"
              AND deleted_at  IS NULL
            """,
            (now,),
        ).fetchall()

        if not rows:
            print(f"[INFO] No reminders due at {now}")
            return

        for row in rows:
            item = dict(row)
            tid  = item["id"]

            msg  = (
                f"\u23f0 <b>\u5f85\u8fa6\u63d0\u9192</b>\n"
                f"\u4efb\u52d9\uff1a{item[title]}\n"
                f"\u8ca0\u8cac\u4eba\uff1a{item[owner_user]}\n"
                f"\u72c0\u614b\uff1a{item[status]}"
            )
            if item.get("deadline_at"):
                msg += f"\n\u622a\u6b62\uff1a{str(item[deadline_at])[:10]}"

            sent = False
            if token and chat_id:
                sent = _send_tg(token, chat_id, msg)
                if sent:
                    print(f"[OK] Telegram sent — todo_id={tid}: {item[title]}")
                else:
                    print(f"[WARN] Telegram failed — todo_id={tid}: {item[title]}")

            if not sent:
                print(f"[REMIND] todo_id={tid}: {item[title]} (owner: {item[owner_user]})")

            conn.execute(
                "UPDATE todo_items SET reminded_at=? WHERE id=?", (now, tid)
            )
            conn.execute(
                "INSERT INTO todo_activity_log"
                "(todo_id, action, actor_user, created_at)"
                " VALUES(?, \"remind_sent\", \"system\", ?)",
                (tid, now),
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
