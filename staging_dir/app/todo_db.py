"""Todo DB helpers — SQLite, configurable db_path via TodoDB class."""
from __future__ import annotations
import json, os, sqlite3
from datetime import datetime
from app.database import DB_PATH, DATA_DIR

class TodoDB:
    def __init__(self, db_path: str):
        if not os.path.isabs(db_path):
            db_path = os.path.join(DATA_DIR, db_path)
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    def _migrate_columns(self) -> None:
        with self._conn() as c:
            for sql in [
                "ALTER TABLE todo_items ADD COLUMN is_private INTEGER NOT NULL DEFAULT 0",
                "ALTER TABLE todo_items ADD COLUMN namespace TEXT NOT NULL DEFAULT 'internal'",
            ]:
                try: c.execute(sql)
                except sqlite3.OperationalError: pass

    def init_todo_tables(self) -> None:
        with self._conn() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS todo_items (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                description TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'open',
                priority INTEGER NOT NULL DEFAULT 2, is_private INTEGER NOT NULL DEFAULT 0,
                owner_user TEXT NOT NULL, created_by TEXT NOT NULL,
                updated_by TEXT NOT NULL, deleted_by TEXT,
                deadline_at TEXT, remind_at TEXT, reminded_at TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT
            );
            CREATE TABLE IF NOT EXISTS todo_tags (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS todo_item_tags (
                todo_id INTEGER NOT NULL, tag_id INTEGER NOT NULL, UNIQUE(todo_id, tag_id)
            );
            CREATE TABLE IF NOT EXISTS todo_activity_log (
                id INTEGER PRIMARY KEY, todo_id INTEGER, action TEXT NOT NULL,
                actor_user TEXT NOT NULL, before_json TEXT, after_json TEXT, created_at TEXT NOT NULL
            );
            """)
        self._migrate_columns()

    def tags_list(self) -> list[dict]:
        self.init_todo_tables()
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM todo_tags ORDER BY name")]

    def tags_upsert(self, names: list[str]) -> list[int]:
        now = self._now(); ids: list[int] = []
        with self._conn() as c:
            for name in names:
                name = name.strip()
                if not name: continue
                c.execute("INSERT OR IGNORE INTO todo_tags(name, created_at) VALUES(?, ?)", (name, now))
                row = c.execute("SELECT id FROM todo_tags WHERE name=?", (name,)).fetchone()
                if row: ids.append(row[0])
        return ids

    def todo_set_tags(self, todo_id: int, tag_ids: list[int]) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM todo_item_tags WHERE todo_id=?", (todo_id,))
            for tid in tag_ids:
                c.execute("INSERT OR IGNORE INTO todo_item_tags(todo_id, tag_id) VALUES(?, ?)", (todo_id, tid))

    def activity_log_append(self, todo_id: int, action: str, actor: str,
                            before: dict | None = None, after: dict | None = None) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO todo_activity_log(todo_id,action,actor_user,before_json,after_json,created_at) VALUES(?,?,?,?,?,?)",
                (todo_id, action, actor,
                 json.dumps(before, ensure_ascii=False) if before is not None else None,
                 json.dumps(after,  ensure_ascii=False) if after  is not None else None,
                 self._now()),
            )

    def activity_log_list(self, todo_id: int, limit: int = 5) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT * FROM todo_activity_log WHERE todo_id=? ORDER BY id DESC LIMIT ?",
                (todo_id, limit)).fetchall()
            return [dict(r) for r in rows]

    def todo_get(self, todo_id: int) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT * FROM todo_items WHERE id=?", (todo_id,)).fetchone()
            if not row: return None
            item = dict(row)
            tags = c.execute(
                "SELECT t.name FROM todo_tags t JOIN todo_item_tags it ON t.id=it.tag_id WHERE it.todo_id=?",
                (todo_id,)).fetchall()
            item["tags"] = [r[0] for r in tags]
            return item

    def todo_create(self, title: str, description: str, status: str, priority: int,
                    owner_user: str, created_by: str, deadline_at: str | None = None,
                    remind_at: str | None = None, tag_names: list[str] | None = None,
                    is_private: int = 0, namespace: str = "internal") -> int:
        now = self._now()
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO todo_items(title,description,status,priority,is_private,namespace,"
                "owner_user,created_by,updated_by,deadline_at,remind_at,created_at,updated_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (title, description, status, priority, is_private, namespace,
                 owner_user, created_by, created_by, deadline_at, remind_at, now, now))
            todo_id = cur.lastrowid
        if tag_names:
            ids = self.tags_upsert(tag_names)
            self.todo_set_tags(todo_id, ids)
        self.activity_log_append(todo_id, "create", created_by,
            after={"title": title, "status": status, "priority": priority, "owner": owner_user})
        return todo_id

    def todo_update(self, todo_id: int, updater: str, tag_names: list[str] | None = None, **fields) -> None:
        before = self.todo_get(todo_id)
        if fields:
            setters = ", ".join(f"{k}=?" for k in fields)
            with self._conn() as c:
                c.execute(f"UPDATE todo_items SET {setters}, updated_at=?, updated_by=? WHERE id=?",
                          list(fields.values()) + [self._now(), updater, todo_id])
        elif tag_names is not None:
            with self._conn() as c:
                c.execute("UPDATE todo_items SET updated_at=?, updated_by=? WHERE id=?",
                          (self._now(), updater, todo_id))
        if tag_names is not None:
            self.todo_set_tags(todo_id, self.tags_upsert(tag_names))
        after = self.todo_get(todo_id)
        action = "status" if "status" in fields else ("tag" if tag_names is not None and not fields else "update")
        log_keys = list(fields.keys()) + (["tags"] if tag_names is not None else [])
        self.activity_log_append(todo_id, action, updater,
            before={k: before.get(k) for k in log_keys} if before else None,
            after={k: after.get(k) for k in log_keys} if after else None)

    def todo_soft_delete(self, todo_id: int, deleter: str) -> None:
        before = self.todo_get(todo_id); now = self._now()
        with self._conn() as c:
            c.execute("UPDATE todo_items SET deleted_at=?,deleted_by=?,updated_at=?,updated_by=? WHERE id=?",
                      (now, deleter, now, deleter, todo_id))
        self.activity_log_append(todo_id, "delete", deleter,
            before={"title": before.get("title")} if before else None)

    def todo_list(self, keyword: str = "", tag_names: list[str] | None = None,
                  status: str = "", mine_user: str = "", include_done: bool = True,
                  sort: str = "updated_desc", current_user: str = "",
                  namespace: str = "internal") -> list[dict]:
        self.init_todo_tables()
        sql = ("SELECT i.*, GROUP_CONCAT(t.name, ',') AS tags_str FROM todo_items i"
               " LEFT JOIN todo_item_tags it ON i.id=it.todo_id"
               " LEFT JOIN todo_tags t ON it.tag_id=t.id"
               " WHERE i.deleted_at IS NULL AND i.namespace=?")
        params: list = [namespace]
        if current_user:
            sql += " AND (i.is_private=0 OR i.created_by=? OR i.owner_user=?)"
            params.extend([current_user, current_user])
        if not include_done: sql += " AND i.status != 'done'"
        if status and status not in ("", "all"): sql += " AND i.status=?"; params.append(status)
        if mine_user: sql += " AND i.owner_user=?"; params.append(mine_user)
        if keyword:
            sql += " AND (i.title LIKE ? OR i.description LIKE ?)"; params.extend([f"%{keyword}%", f"%{keyword}%"])
        sql += " GROUP BY i.id"
        if tag_names:
            ph = ",".join("?" * len(tag_names))
            sql += f" HAVING SUM(CASE WHEN t.name IN ({ph}) THEN 1 ELSE 0 END) > 0"
            params.extend(tag_names)
        _sort_clause = {'updated_desc': 'i.updated_at DESC', 'deadline_asc': 'CASE WHEN i.deadline_at IS NULL THEN 1 ELSE 0 END, i.deadline_at ASC', 'priority_asc': 'i.priority ASC, i.updated_at DESC'}.get(sort, 'i.updated_at DESC')
        sql += f" ORDER BY {_sort_clause}"
        with self._conn() as c:
            rows = c.execute(sql, params).fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item["tags"] = [t for t in (item.get("tags_str") or "").split(",") if t]
            result.append(item)
        return result


# ── Backward-compat module-level bindings (04_待辦.py 不需要改) ──────────────
_default_db         = TodoDB(DB_PATH)
init_todo_tables    = _default_db.init_todo_tables
tags_list           = _default_db.tags_list
tags_upsert         = _default_db.tags_upsert
todo_set_tags       = _default_db.todo_set_tags
activity_log_append = _default_db.activity_log_append
activity_log_list   = _default_db.activity_log_list
todo_get            = _default_db.todo_get
todo_create         = _default_db.todo_create
todo_update         = _default_db.todo_update
todo_soft_delete    = _default_db.todo_soft_delete
todo_list           = _default_db.todo_list
