"""rolling_db.py — Rolling Group Availability DB helpers (SQLite, same menu.db)."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

from app.database import DB_PATH

SLOTS = ["morning", "noon", "evening"]
SLOT_LABEL = {"morning": "早上", "noon": "中午", "evening": "晚上"}
STATE_ICON = {"YES": "✅", "NO": "⬜", "MAYBE": "🔶"}
STATE_CYCLE_MAYBE = {"NO": "YES", "YES": "MAYBE", "MAYBE": "NO"}
STATE_CYCLE_PLAIN = {"NO": "YES", "YES": "NO",    "MAYBE": "NO"}


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


# ── Schema ─────────────────────────────────────────────────────────────────────

def init_rolling_tables() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS rolling_group (
            id          INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            owner_email TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'ACTIVE',
            allow_maybe INTEGER NOT NULL DEFAULT 0,
            mode        TEXT    NOT NULL DEFAULT 'ALL',
            threshold_n INTEGER,
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rolling_member (
            id           INTEGER PRIMARY KEY,
            group_id     INTEGER NOT NULL,
            user_email   TEXT    NOT NULL,
            display_name TEXT    NOT NULL DEFAULT '',
            role         TEXT    NOT NULL DEFAULT 'MEMBER',
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL,
            UNIQUE(group_id, user_email),
            FOREIGN KEY(group_id) REFERENCES rolling_group(id)
        );

        CREATE TABLE IF NOT EXISTS rolling_availability (
            group_id   INTEGER NOT NULL,
            user_email TEXT    NOT NULL,
            date       TEXT    NOT NULL,
            slot       TEXT    NOT NULL,
            state      TEXT    NOT NULL DEFAULT 'NO',
            updated_at TEXT    NOT NULL,
            UNIQUE(group_id, user_email, date, slot),
            FOREIGN KEY(group_id) REFERENCES rolling_group(id)
        );
        """)


# ── Group ──────────────────────────────────────────────────────────────────────

def group_create(
    name: str,
    description: str,
    owner_email: str,
    allow_maybe: bool = False,
    mode: str = "ALL",
    threshold_n: Optional[int] = None,
) -> int:
    now = _now()
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO rolling_group"
            "(name, description, owner_email, status, allow_maybe, mode, threshold_n, created_at, updated_at)"
            " VALUES(?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?)",
            (name, description, owner_email, 1 if allow_maybe else 0, mode, threshold_n, now, now),
        )
        group_id = cur.lastrowid
    member_add(group_id, owner_email, owner_email.split("@")[0], role="OWNER")
    return group_id


def group_get(group_id: int) -> Optional[dict]:
    init_rolling_tables()
    with _conn() as c:
        row = c.execute("SELECT * FROM rolling_group WHERE id=?", (group_id,)).fetchone()
        return dict(row) if row else None


def group_list_for_user(user_email: str) -> list[dict]:
    init_rolling_tables()
    with _conn() as c:
        rows = c.execute(
            """SELECT g.* FROM rolling_group g
               JOIN rolling_member m ON g.id = m.group_id
               WHERE m.user_email=? AND g.status='ACTIVE'
               ORDER BY g.created_at DESC""",
            (user_email,),
        ).fetchall()
        return [dict(r) for r in rows]


def group_update(group_id: int, **fields) -> None:
    if not fields:
        return
    fields["updated_at"] = _now()
    setters = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [group_id]
    with _conn() as c:
        c.execute(f"UPDATE rolling_group SET {setters} WHERE id=?", vals)


def group_archive(group_id: int) -> None:
    group_update(group_id, status="ARCHIVED")


# ── Members ────────────────────────────────────────────────────────────────────

def member_add(
    group_id: int,
    user_email: str,
    display_name: str = "",
    role: str = "MEMBER",
) -> None:
    now = _now()
    dn = display_name or user_email.split("@")[0]
    with _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO rolling_member"
            "(group_id, user_email, display_name, role, created_at, updated_at)"
            " VALUES(?, ?, ?, ?, ?, ?)",
            (group_id, user_email, dn, role, now, now),
        )


def member_remove(group_id: int, user_email: str) -> None:
    with _conn() as c:
        c.execute(
            "DELETE FROM rolling_member WHERE group_id=? AND user_email=?",
            (group_id, user_email),
        )


def member_list(group_id: int) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM rolling_member WHERE group_id=? ORDER BY role DESC, created_at ASC",
            (group_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def is_owner(group_id: int, user_email: str) -> bool:
    with _conn() as c:
        row = c.execute(
            "SELECT id FROM rolling_member WHERE group_id=? AND user_email=? AND role='OWNER'",
            (group_id, user_email),
        ).fetchone()
        return row is not None


# ── Availability ───────────────────────────────────────────────────────────────

def availability_upsert(
    group_id: int,
    user_email: str,
    date_str: str,
    slot: str,
    state: str,
) -> None:
    now = _now()
    with _conn() as c:
        c.execute(
            """INSERT INTO rolling_availability(group_id, user_email, date, slot, state, updated_at)
               VALUES(?, ?, ?, ?, ?, ?)
               ON CONFLICT(group_id, user_email, date, slot) DO UPDATE SET
                 state=excluded.state, updated_at=excluded.updated_at""",
            (group_id, user_email, date_str, slot, state, now),
        )


def availability_matrix(
    group_id: int,
    user_email: str,
    date_list: list[str],
) -> dict[tuple[str, str], str]:
    """Return {(date, slot): state} for one user. Missing = 'NO'."""
    if not date_list:
        return {}
    ph = ",".join("?" * len(date_list))
    with _conn() as c:
        rows = c.execute(
            f"SELECT date, slot, state FROM rolling_availability"
            f" WHERE group_id=? AND user_email=? AND date IN ({ph})",
            [group_id, user_email] + date_list,
        ).fetchall()
    return {(r["date"], r["slot"]): r["state"] for r in rows}


def intersection_compute(
    group_id: int,
    date_list: list[str],
) -> dict[tuple[str, str], dict]:
    """Return {(date, slot): {"yes_count": N, "total_members": M}} for the window."""
    members = member_list(group_id)
    total = len(members)
    if not date_list:
        return {}
    ph = ",".join("?" * len(date_list))
    with _conn() as c:
        rows = c.execute(
            f"SELECT date, slot, state FROM rolling_availability"
            f" WHERE group_id=? AND date IN ({ph})",
            [group_id] + date_list,
        ).fetchall()

    counts: dict[tuple[str, str], int] = {}
    for r in rows:
        if r["state"] == "YES":
            key = (r["date"], r["slot"])
            counts[key] = counts.get(key, 0) + 1

    result = {}
    for d in date_list:
        for s in SLOTS:
            key = (d, s)
            result[key] = {"yes_count": counts.get(key, 0), "total_members": total}
    return result


def availability_who_yes(
    group_id: int,
    date_list: list[str],
) -> dict[tuple[str, str], list[dict]]:
    """Return {(date, slot): [{user_email, display_name}, ...]} for YES responses."""
    if not date_list:
        return {}
    ph = ",".join("?" * len(date_list))
    with _conn() as c:
        rows = c.execute(
            f"""SELECT a.date, a.slot, a.user_email, COALESCE(m.display_name, a.user_email) AS display_name
                FROM rolling_availability a
                LEFT JOIN rolling_member m ON m.group_id = a.group_id AND m.user_email = a.user_email
                WHERE a.group_id=? AND a.date IN ({ph}) AND a.state='YES'""",
            [group_id] + date_list,
        ).fetchall()
    result: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = (r["date"], r["slot"])
        result.setdefault(key, []).append(
            {"user_email": r["user_email"], "display_name": r["display_name"]}
        )
    return result


def group_list_joinable(user_email: str) -> list[dict]:
    """Return all ACTIVE groups the user is NOT already a member of."""
    init_rolling_tables()
    with _conn() as c:
        rows = c.execute(
            """SELECT g.* FROM rolling_group g
               WHERE g.status='ACTIVE'
               AND g.id NOT IN (
                   SELECT group_id FROM rolling_member WHERE user_email=?
               )
               ORDER BY g.created_at DESC""",
            (user_email,),
        ).fetchall()
        return [dict(r) for r in rows]
