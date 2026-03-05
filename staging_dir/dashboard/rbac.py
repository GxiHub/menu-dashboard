"""rbac.py — 身份驗證 + 角色權限（DB 驅動）"""
from __future__ import annotations

import base64
import json
import os
import sqlite3
from datetime import datetime

import streamlit as st

# ── 常數 ──────────────────────────────────────────────────────────────────────
ADMIN_EMAIL = "miniblackeye@gmail.com"

_CF_HEADER = "Cf-Access-Authenticated-User-Email"
_CF_COOKIE = "CF_Authorization"

# 每個角色可訪問的頁面（set-based，非線性層級）
ROLE_PAGES: dict[str, set] = {
    "blocked": set(),
    "level1":  {"待辦1"},
    "level2":  {"待辦1", "行事曆"},
    "level3":  {"待辦1", "行事曆", "顯示"},
    "level4":  {"待辦1", "行事曆", "顯示", "待辦2"},
    "level5":  {"待辦1", "行事曆", "顯示", "待辦2", "待辦3"},
    "level6":  {"待辦1", "行事曆", "顯示", "待辦2", "待辦3", "待辦4"},
    "viewer":  {"顯示"},
    "editor":  {"顯示", "待辦", "待辦1", "行事曆"},
    "admin":   {"顯示", "簡報", "待辦", "待辦1", "待辦2", "待辦3", "待辦4", "待辦5", "行事曆", "社團爬蟲", "管理"},
}

# 所有可設定頁面
ALL_PAGES = ["顯示", "簡報", "待辦", "待辦1", "待辦2", "待辦3", "待辦4", "待辦5", "行事曆", "日常表", "社團爬蟲", "管理"]

ROLE_LABEL = {
    "blocked": "🚫 封鎖",
    "level1":  "Lv1 待辦1",
    "level2":  "Lv2 待辦1",
    "level3":  "Lv3 待辦1",
    "level4":  "Lv4 待辦1",
    "level5":  "Lv5 待辦1",
    "level6":  "Lv6 待辦1",
    "viewer":  "👁 訪客（僅顯示）",
    "editor":  "✏️ 編輯",
    "admin":   "👑 管理員",
}

# 下拉選單順序
ROLE_OPTIONS = ["blocked", "level1", "level2", "level3", "level4", "level5", "level6", "viewer", "editor", "admin"]

# ── DB ─────────────────────────────────────────────────────────────────────────
def _db() -> str:
    base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, "data", "menu.db")

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(_db())
    c.row_factory = sqlite3.Row
    return c

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def init_permission_tables() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id          INTEGER PRIMARY KEY,
            user_email  TEXT NOT NULL UNIQUE,
            role        TEXT NOT NULL DEFAULT 'viewer',
            note        TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            updated_by  TEXT NOT NULL DEFAULT 'system'
        );
        CREATE TABLE IF NOT EXISTS user_access_log (
            id          INTEGER PRIMARY KEY,
            user_email  TEXT NOT NULL,
            page        TEXT NOT NULL,
            accessed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS role_page_permissions (
            role TEXT NOT NULL,
            page TEXT NOT NULL,
            PRIMARY KEY (role, page)
        );
        """)
    _seed_role_pages()

# ── 角色頁面設定（DB 驅動）─────────────────────────────────────────────────────
def _seed_role_pages() -> None:
    """若表格為空，以 ROLE_PAGES 預設值初始化。"""
    with _conn() as c:
        count = c.execute("SELECT COUNT(*) FROM role_page_permissions").fetchone()[0]
    if count == 0:
        for role, pages in ROLE_PAGES.items():
            with _conn() as c:
                for page in pages:
                    c.execute(
                        "INSERT OR IGNORE INTO role_page_permissions(role, page) VALUES(?,?)",
                        (role, page)
                    )

def get_role_pages(role: str) -> set:
    """從 DB 讀取角色允許的頁面。若 DB 無資料，回退至 ROLE_PAGES 預設值。"""
    with _conn() as c:
        rows = c.execute(
            "SELECT page FROM role_page_permissions WHERE role=?", (role,)
        ).fetchall()
    if rows:
        return {r[0] for r in rows}
    return ROLE_PAGES.get(role, set())

def set_role_pages(role: str, pages: set, by: str) -> None:
    """取代某角色的所有頁面權限。admin 永遠保留「管理」；blocked 永遠無頁面。"""
    if role == "admin":
        pages = pages | {"管理"}
    if role == "blocked":
        pages = set()
    with _conn() as c:
        c.execute("DELETE FROM role_page_permissions WHERE role=?", (role,))
        for page in pages:
            c.execute(
                "INSERT INTO role_page_permissions(role, page) VALUES(?,?)",
                (role, page)
            )

# ── 身份 ────────────────────────────────────────────────────────────────────────
def _decode_cf_jwt(token: str) -> str:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return ""
        padding = (4 - len(parts[1]) % 4) % 4
        payload = base64.urlsafe_b64decode(parts[1] + "=" * padding)
        return json.loads(payload).get("email", "")
    except Exception:
        return ""

def get_user_email() -> str:
    try:
        email = st.context.headers.get(_CF_HEADER, "")
        if email:
            return email
    except Exception:
        pass
    try:
        cookie = st.context.cookies.get(_CF_COOKIE, "")
        if cookie:
            return _decode_cf_jwt(cookie)
    except Exception:
        pass
    return ""

# ── 角色 ────────────────────────────────────────────────────────────────────────
def get_user_role(email: str) -> str:
    """取得 email 的角色。admin 永遠是 admin；新用戶預設 viewer。"""
    if not email:
        return "blocked"
    if email == ADMIN_EMAIL:
        return "admin"
    init_permission_tables()
    with _conn() as c:
        row = c.execute(
            "SELECT role FROM user_permissions WHERE user_email=?", (email,)
        ).fetchone()
    if row:
        return row["role"]
    # 第一次登入：自動建立 viewer 記錄
    _upsert_user(email, "viewer", "system")
    return "viewer"

def _upsert_user(email: str, role: str, by: str) -> None:
    now = _now()
    with _conn() as c:
        c.execute("""
            INSERT INTO user_permissions(user_email, role, created_at, updated_at, updated_by)
            VALUES(?,?,?,?,?)
            ON CONFLICT(user_email) DO UPDATE SET
              role=excluded.role, updated_at=excluded.updated_at, updated_by=excluded.updated_by
        """, (email, role, now, now, by))

def set_user_role(email: str, role: str, by: str) -> None:
    if email == ADMIN_EMAIL:
        return  # admin 不可被降級
    _upsert_user(email, role, by)

# ── 權限檢查 ───────────────────────────────────────────────────────────────────
def require_login() -> str:
    """任何有 email 的登入者，回傳 email；否則 stop。"""
    email = get_user_email()
    if not email:
        st.error("Authentication required via Cloudflare Access.")
        st.stop()
    return email

def require_page(page: str) -> str:
    """
    檢查目前使用者是否有權限進入此頁面。
    回傳 email；不符合則顯示錯誤並 stop。
    """
    email = require_login()
    role   = get_user_role(email)
    allowed_pages = get_role_pages(role)  # DB 驅動
    if page not in allowed_pages:
        needed_lbl = f"可訪問「{page}」的角色"
        role_lbl   = ROLE_LABEL.get(role, role)
        st.markdown(
            f'''<div style="max-width:400px;margin:80px auto;background:white;border-radius:18px;
padding:32px 28px;box-shadow:0 4px 24px rgba(0,0,0,0.10);text-align:center">
<div style="font-size:2.4rem;margin-bottom:12px">🚫</div>
<div style="font-size:1.1rem;font-weight:800;color:#1a1a1a;margin-bottom:8px">權限不足</div>
<div style="font-size:0.88rem;color:#555;margin-bottom:14px">
  此頁面需要 <strong>{needed_lbl}</strong> 以上權限
</div>
<div style="background:#f5f5f5;border-radius:10px;padding:9px 14px;
font-size:0.82rem;color:#888;display:inline-block">
  目前角色：{role_lbl}
</div>
<div style="margin-top:18px;font-size:0.76rem;color:#bbb">請聯絡管理員開通權限</div>
</div>''',
            unsafe_allow_html=True,
        )
        st.stop()
    return email

# 向下相容舊呼叫
def require_editor() -> None:
    require_page("待辦")

def require_admin() -> None:
    require_page("管理")

# ── Access log ─────────────────────────────────────────────────────────────────
def log_access(user_email: str, page: str) -> None:
    if not user_email:
        return
    session_key = f"_logged_{page}"
    if st.session_state.get(session_key):
        return
    st.session_state[session_key] = True
    try:
        init_permission_tables()
        with _conn() as c:
            c.execute(
                "INSERT INTO user_access_log(user_email, page, accessed_at) VALUES(?,?,?)",
                (user_email, page, _now()),
            )
    except Exception:
        pass

def access_log_summary() -> list[dict]:
    try:
        init_permission_tables()
        with _conn() as c:
            rows = c.execute("""
                SELECT l.user_email,
                       COUNT(*) AS visit_count,
                       MAX(l.accessed_at) AS last_seen,
                       GROUP_CONCAT(DISTINCT l.page) AS pages,
                       COALESCE(p.role, 'blocked') AS role
                FROM user_access_log l
                LEFT JOIN user_permissions p ON p.user_email = l.user_email
                GROUP BY l.user_email
                ORDER BY last_seen DESC
            """).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

def permission_list() -> list[dict]:
    """所有已知 user（含 access log 中出現過的），附帶目前角色。"""
    try:
        init_permission_tables()
        with _conn() as c:
            rows = c.execute("""
                SELECT u.user_email,
                       u.role,
                       u.note,
                       u.updated_at,
                       u.updated_by,
                       MAX(l.accessed_at) AS last_seen,
                       COUNT(l.id) AS visit_count
                FROM user_permissions u
                LEFT JOIN user_access_log l ON l.user_email = u.user_email
                GROUP BY u.user_email
                ORDER BY last_seen DESC NULLS LAST
            """).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

def access_log_recent(limit: int = 50) -> list[dict]:
    try:
        with _conn() as c:
            rows = c.execute(
                "SELECT * FROM user_access_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []
