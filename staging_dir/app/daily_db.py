"""daily_db.py — 半小時日常時間表 DB 操作"""
from __future__ import annotations
import os
import sqlite3
from datetime import datetime


def _db() -> str:
    base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, "data", "menu.db")


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(_db())
    c.row_factory = sqlite3.Row
    return c


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


_DEFAULT_TAGS = ["睡眠", "工作", "學習", "休息", "吃飯", "運動", "通勤", "娛樂"]

SLEEP_SLOTS: frozenset[str] = frozenset(
    f"{h:02d}:{m:02d}"
    for h in list(range(0, 7)) + [23]
    for m in (0, 30)
)


def init_daily_tables() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS daily_tags (
            id         INTEGER PRIMARY KEY,
            name       TEXT NOT NULL UNIQUE,
            created_by TEXT NOT NULL DEFAULT 'system',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS daily_schedule (
            id         INTEGER PRIMARY KEY,
            date       TEXT NOT NULL,
            slot       TEXT NOT NULL,
            content    TEXT NOT NULL DEFAULT '',
            user_email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(date, slot, user_email)
        );
        """)
    _seed_tags()


def _seed_tags() -> None:
    with _conn() as c:
        count = c.execute("SELECT COUNT(*) FROM daily_tags").fetchone()[0]
        if count == 0:
            now = _now()
            for tag in _DEFAULT_TAGS:
                c.execute(
                    "INSERT OR IGNORE INTO daily_tags(name, created_by, created_at) VALUES(?,?,?)",
                    (tag, "system", now)
                )


def get_tags() -> list[str]:
    with _conn() as c:
        rows = c.execute("SELECT name FROM daily_tags ORDER BY id").fetchall()
    return [r[0] for r in rows]


def get_tags_with_id() -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT id, name FROM daily_tags ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def add_tag(name: str, created_by: str) -> bool:
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO daily_tags(name, created_by, created_at) VALUES(?,?,?)",
                (name.strip(), created_by, _now())
            )
        return True
    except Exception:
        return False


def delete_tag(tag_id: int) -> None:
    with _conn() as c:
        c.execute("DELETE FROM daily_tags WHERE id=?", (tag_id,))


def get_schedule(date_str: str, user_email: str) -> dict[str, str]:
    with _conn() as c:
        rows = c.execute(
            "SELECT slot, content FROM daily_schedule WHERE date=? AND user_email=?",
            (date_str, user_email)
        ).fetchall()
    return {r["slot"]: r["content"] for r in rows}


def save_slot(date_str: str, slot: str, content: str, user_email: str) -> None:
    now = _now()
    content = (content or "").strip()
    with _conn() as c:
        if content:
            c.execute("""
                INSERT INTO daily_schedule(date, slot, content, user_email, created_at, updated_at)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(date, slot, user_email) DO UPDATE SET
                    content=excluded.content, updated_at=excluded.updated_at
            """, (date_str, slot, content, user_email, now, now))
        else:
            c.execute(
                "DELETE FROM daily_schedule WHERE date=? AND slot=? AND user_email=?",
                (date_str, slot, user_email)
            )
