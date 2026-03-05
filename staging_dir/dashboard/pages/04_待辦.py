"""04_todo.py — 多人待辦清單頁面 v2.0 (Dribbble card-style UI)"""
from __future__ import annotations

import json
from datetime import date, datetime

import streamlit as st

from ui_common import apply_base_css, render_sidebar_admin
from rbac import require_page, get_user_email, log_access
from app.todo_db import (
    init_todo_tables, tags_list, todo_create, todo_update,
    todo_soft_delete, todo_list, activity_log_list,
)

# ── constants ─────────────────────────────────────────────────────────────────

STATUSES = ["open", "doing", "blocked", "done"]
STATUS_LABEL = {"open": "待辦", "doing": "進行中", "blocked": "封鎖", "done": "完成"}
STATUS_ICON  = {"open": "⬜", "doing": "▶️", "blocked": "⏸", "done": "✅"}
PRIORITY_LABEL = {1: "🔴 高", 2: "🟡 中", 3: "🟢 低"}
PRIORITY_INT   = {"🔴 高": 1, "🟡 中": 2, "🟢 低": 3}
ACTION_LABEL   = {
    "create": "建立任務", "update": "更新", "delete": "刪除",
    "status": "變更狀態", "tag": "更新標籤", "remind_sent": "提醒已發送",
}

# ── page setup ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="待辦清單｜菜單儀表板", layout="wide")
user = require_page("待辦")
log_access(user, "待辦")
apply_base_css()
render_sidebar_admin()
init_todo_tables()

user_short = user.split("@")[0]

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* === Background === */
.stApp { background-color: #f0f2f5 !important; }
.block-container { padding-top: 4rem !important; max-width: 900px !important; }

/* === Page header === */
.page-title    { font-size: 1.85rem; font-weight: 800; color: #1a1a1a; line-height: 1.2; margin: 0; }
.page-subtitle { font-size: 0.88rem; color: #9e9e9e; margin-top: 3px; }

/* === Primary green button === */
button[kind="primary"] {
    background-color: #3dba6e !important;
    border-color: #3dba6e !important;
    border-radius: 99px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(61,186,110,0.3) !important;
}
button[kind="primary"]:hover {
    background-color: #34a862 !important;
    border-color: #34a862 !important;
}

/* === Status tabs === */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    border-bottom: 2px solid #e8e8e8 !important;
    background: transparent !important;
    padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 7px 18px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    color: #9e9e9e !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #2ea85a !important;
    background: white !important;
    border-bottom: 2px solid #3dba6e !important;
    font-weight: 700 !important;
}
.stTabs [data-testid="stTabsContent"] {
    padding-top: 14px !important;
    border: none !important;
    background: transparent !important;
}

/* === Expander as card === */
[data-testid="stExpander"] {
    background: white !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
    transition: box-shadow 0.15s !important;
}
[data-testid="stExpander"]:hover {
    box-shadow: 0 4px 18px rgba(0,0,0,0.10) !important;
}
[data-testid="stExpander"] summary {
    padding: 15px 20px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    background: white !important;
    border-radius: 16px 16px 0 0 !important;
}
[data-testid="stExpander"] summary:hover { background: #fafafa !important; }
[data-testid="stExpander"] > details { border: none !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 2px 20px 18px 20px !important;
}

/* === Task meta & badges === */
.todo-meta { color: #9e9e9e; font-size: 0.80rem; margin-bottom: 8px; line-height: 1.6; }
.status-pill {
    display: inline-block; border-radius: 99px;
    padding: 2px 10px; font-size: 0.73rem; font-weight: 600;
}
.sp-open    { background: #f0f0f0; color: #888; }
.sp-doing   { background: #eff6ff; color: #3b82f6; }
.sp-blocked { background: #fef2f2; color: #ef4444; }
.sp-done    { background: #e8f5ee; color: #2ea85a; }
.overdue-badge {
    display: inline-block; background: #fef2f2; color: #ef4444;
    border-radius: 4px; padding: 1px 7px;
    font-size: 0.72rem; font-weight: 700; margin-left: 6px; vertical-align: middle;
}
.tag-pill {
    display: inline-block; background: #e0e7ff; color: #3730a3;
    border-radius: 99px; padding: 2px 10px;
    font-size: 0.72rem; font-weight: 500; margin-right: 4px; margin-bottom: 2px;
}

/* === Search & filter inputs === */
.stTextInput > div > div > input {
    border-radius: 12px !important; background: white !important;
    border-color: #e8e8e8 !important; font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3dba6e !important;
    box-shadow: 0 0 0 2px rgba(61,186,110,0.15) !important;
}
.stSelectbox > div > div { border-radius: 12px !important; background: white !important; }
.stMultiSelect > div { border-radius: 12px !important; background: white !important; }
.stRadio > div { gap: 4px !important; }
.stRadio label { font-size: 0.85rem !important; }

/* === Action buttons inside card === */
[data-testid="stExpander"] .stButton > button[kind="secondary"] {
    border-radius: 8px !important; font-size: 0.80rem !important;
    border-color: #e8e8e8 !important; color: #555 !important; padding: 4px 12px !important;
}

/* === Private badge === */
.sp-private { background: #f5f3ff; color: #7c3aed; }

/* === Empty state === */
.empty-todo { text-align: center; padding: 48px 20px; color: #bbb; }
.empty-todo-icon { font-size: 2.5rem; }
.empty-todo-text { font-size: 0.9rem; margin-top: 8px; }

/* === Dividers === */
hr { border-color: #f0f0f0 !important; margin: 10px 0 !important; }
.stAlert { border-radius: 12px !important; }
.stCheckbox > label { font-size: 0.85rem !important; color: #666 !important; }
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def _is_overdue(task: dict) -> bool:
    if task.get("status") == "done" or not task.get("deadline_at"):
        return False
    return str(task["deadline_at"])[:19] < _now_str()

def _is_soon(task: dict) -> bool:
    """截止時間在 24 小時內但尚未逾期。"""
    if task.get("status") == "done" or not task.get("deadline_at"):
        return False
    try:
        from datetime import datetime, timedelta
        dl  = datetime.fromisoformat(str(task["deadline_at"])[:19])
        now = datetime.now()
        return now < dl <= now + timedelta(hours=24)
    except Exception:
        return False

def _fmt_dt(s: str | None) -> str:
    if not s:
        return "—"
    try:
        if "T" in s:
            return datetime.fromisoformat(s).strftime("%m/%d %H:%M")
        return datetime.fromisoformat(s).strftime("%m/%d")
    except Exception:
        return s[:10]

def _parse_tags_input(raw: str) -> list[str]:
    return [t.strip() for t in raw.replace("，", ",").split(",") if t.strip()]

def _date_or_none(d) -> str | None:
    return None if d is None else str(d)
TIME_OPTS = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]

def _datetime_or_none(d, t: str) -> str | None:
    """合併日期 + 時間字串，日期為 None 時回傳 None。"""
    if d is None:
        return None
    return f"{d}T{t}:00"

def _time_index(dt_str) -> int:
    """從 datetime 字串取得最近半小時對應的 TIME_OPTS index。"""
    if not dt_str or "T" not in str(dt_str):
        return 16  # 預設 08:00
    try:
        t = str(dt_str)[11:16]
        h, m = int(t[:2]), int(t[3:5])
        m = 0 if m < 30 else 30
        return h * 2 + (1 if m == 30 else 0)
    except Exception:
        return 16


def _render_activity(log: list[dict]) -> None:
    if not log:
        st.caption("（尚無活動記錄）")
        return
    for entry in log:
        action = ACTION_LABEL.get(entry["action"], entry["action"])
        ts     = _fmt_dt(entry["created_at"])
        actor  = entry["actor_user"].split("@")[0]
        extra  = ""
        if entry["action"] == "status":
            try:
                b  = json.loads(entry.get("before_json") or "{}")
                a  = json.loads(entry.get("after_json")  or "{}")
                bs = STATUS_LABEL.get(b.get("status", ""), "?")
                as_= STATUS_LABEL.get(a.get("status", ""), "?")
                extra = f"（{bs} → {as_}）"
            except Exception:
                pass
        st.caption(f"• **{actor}** {action}{extra}　{ts}")

# ── task card renderer ────────────────────────────────────────────────────────

def _render_task_card(task: dict, tab_key: str) -> None:
    tid     = task["id"]
    overdue = _is_overdue(task)
    status  = task["status"]

    # Expander label: status icon + ⚠ prefix if overdue + 🔒 if private + title
    lock_prefix = "🔒 " if task.get("is_private") else ""
    exp_label = f"{'⚠️ ' if overdue else ''}{lock_prefix}{STATUS_ICON[status]}  {task['title']}"

    with st.expander(exp_label, expanded=False):

        # ── meta + badges ──
        pri_lbl  = PRIORITY_LABEL.get(task["priority"], "🟡 中")
        owner_s  = task["owner_user"].split("@")[0]
        sp_cls   = f"sp-{status}"
        stat_pill = f'<span class="status-pill {sp_cls}">{STATUS_ICON[status]} {STATUS_LABEL[status]}</span>'
        ob_badge  = '<span class="overdue-badge">⚠ 逾期</span>' if overdue else ""

        meta_parts = [pri_lbl, f"👤 {owner_s}"]
        meta_line = " &nbsp;·&nbsp; ".join(meta_parts)

        tags_html = "".join(
            f'<span class="tag-pill">{t}</span>' for t in task.get("tags", [])
        )
        private_badge = '<span class="status-pill sp-private">🔒 私人</span> &nbsp; ' if task.get("is_private") else ""

        # ── 截止日期：獨立大字色塊 ──
        dl_html = ""
        if task.get("deadline_at"):
            dl_str = _fmt_dt(task["deadline_at"])
            if task.get("status") == "done":
                dl_html = (
                    f'<div style="display:inline-block;background:#f5f5f5;color:#bbb;'                    f'border-radius:10px;padding:5px 16px;font-size:1rem;font-weight:700;'                    f'margin:6px 0 4px 0;text-decoration:line-through;">📅 {dl_str}</div>'
                )
            elif overdue:
                dl_html = (
                    f'<div style="display:inline-flex;align-items:center;gap:8px;'                    f'background:#fef2f2;color:#ef4444;border-radius:10px;'                    f'padding:5px 16px;font-size:1.1rem;font-weight:800;margin:6px 0 4px 0;">'                    f'📅 {dl_str}'                    f'<span style="font-size:0.7rem;background:#ef4444;color:white;'                    f'border-radius:4px;padding:1px 7px;">逾期</span></div>'
                )
            elif _is_soon(task):
                dl_html = (
                    f'<div style="display:inline-flex;align-items:center;gap:8px;'                    f'background:#fff7ed;color:#ea580c;border-radius:10px;'                    f'padding:5px 16px;font-size:1.1rem;font-weight:800;margin:6px 0 4px 0;">'                    f'📅 {dl_str}'                    f'<span style="font-size:0.7rem;background:#ea580c;color:white;'                    f'border-radius:4px;padding:1px 7px;">即將到期</span></div>'
                )
            else:
                dl_html = (
                    f'<div style="display:inline-block;background:#eff6ff;color:#3b82f6;'                    f'border-radius:10px;padding:5px 16px;font-size:1.1rem;font-weight:800;'                    f'margin:6px 0 4px 0;">📅 {dl_str}</div>'
                )

        st.markdown(
            f'<div class="todo-meta">{private_badge}{stat_pill} &nbsp; {meta_line}{ob_badge}</div>'
            + dl_html
            + (f'<div style="margin-bottom:8px;margin-top:4px">{tags_html}</div>' if tags_html else ""),
            unsafe_allow_html=True,
        )

        if task.get("description"):
            st.markdown(task["description"])

        st.divider()

        # ── quick status buttons ──
        st.markdown("**切換狀態：**")
        btn_cols = st.columns(4)
        for i, s in enumerate(STATUSES):
            with btn_cols[i]:
                if st.button(
                    f"{STATUS_ICON[s]} {STATUS_LABEL[s]}",
                    key=f"{tab_key}_qs_{s}_{tid}",
                    disabled=(status == s),
                    use_container_width=True,
                ):
                    todo_update(tid, user, status=s)
                    st.rerun()

        st.divider()

        # ── edit / delete buttons ──
        edit_key = f"{tab_key}_editing_{tid}"
        del_key  = f"{tab_key}_del_{tid}"

        can_edit = (task["owner_user"] == user or task["created_by"] == user)
        col_e, col_d = st.columns(2)
        with col_e:
            if can_edit and st.button("✏️ 編輯", key=f"{tab_key}_edit_btn_{tid}"):
                st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                st.rerun()
            elif not can_edit:
                st.caption("（唯讀）")
        with col_d:
            if can_edit and not st.session_state.get(del_key):
                if st.button("🗑️ 刪除", key=f"{tab_key}_del_btn_{tid}"):
                    st.session_state[del_key] = True
                    st.rerun()

        # ── edit form ──
        if st.session_state.get(edit_key, False):
            with st.form(f"{tab_key}_edit_form_{tid}"):
                ef1, ef2 = st.columns([4, 1])
                with ef1:
                    e_title = st.text_area("標題", value=task["title"], height=68)
                with ef2:
                    e_priority = st.selectbox(
                        "優先度", list(PRIORITY_LABEL.values()),
                        index=task["priority"] - 1,
                    )
                e_desc = st.text_area("描述", value=task.get("description", ""), height=68)

                ef3, ef4 = st.columns(2)
                with ef3:
                    e_owner  = st.text_input("負責人", value=task["owner_user"])
                    e_status = st.selectbox(
                        "狀態", STATUSES,
                        index=STATUSES.index(task["status"]),
                        format_func=lambda x: f"{STATUS_ICON[x]} {STATUS_LABEL[x]}",
                    )
                with ef4:
                    e_dl_val = None
                    if task.get("deadline_at"):
                        try:
                            e_dl_val = date.fromisoformat(str(task["deadline_at"])[:10])
                        except Exception:
                            pass
                    e_deadline_d = st.date_input("截止日期", value=e_dl_val)
                    e_deadline_t = st.selectbox("截止時間", TIME_OPTS, index=_time_index(task.get("deadline_at")), key=f"e_dl_t_{tid}", label_visibility="collapsed")

                    e_rm_val = None
                    if task.get("remind_at"):
                        try:
                            e_rm_val = date.fromisoformat(str(task["remind_at"])[:10])
                        except Exception:
                            pass
                    e_remind_d   = st.date_input("提醒日期", value=e_rm_val)
                    e_remind_t   = st.selectbox("提醒時間", TIME_OPTS, index=_time_index(task.get("remind_at")), key=f"e_rm_t_{tid}", label_visibility="collapsed")

                e_tags_raw = st.text_input(
                    "標籤（逗號分隔）", value=", ".join(task.get("tags", []))
                )
                e_private = st.checkbox(
                    "🔒 私人任務（僅自己可見）",
                    value=bool(task.get("is_private", 0)),
                )

                sc1, sc2 = st.columns(2)
                with sc1:
                    save_ok   = st.form_submit_button("💾 儲存", type="primary", use_container_width=True)
                with sc2:
                    cancel_ok = st.form_submit_button("取消", use_container_width=True)

                if save_ok:
                    todo_update(
                        tid, user,
                        title=e_title.strip().replace("\n", " "),
                        description=e_desc.strip(),
                        status=e_status,
                        priority=PRIORITY_INT[e_priority],
                        owner_user=e_owner.strip() or user,
                        deadline_at=_datetime_or_none(e_deadline_d, e_deadline_t),
                        remind_at=_datetime_or_none(e_remind_d, e_remind_t),
                        is_private=1 if e_private else 0,
                        tag_names=_parse_tags_input(e_tags_raw),
                    )
                    st.session_state[edit_key] = False
                    st.success("✅ 已更新")
                    st.rerun()
                if cancel_ok:
                    st.session_state[edit_key] = False
                    st.rerun()

        # ── delete confirm ──
        if st.session_state.get(del_key):
            st.warning("確定刪除這項任務？（軟刪除，資料保留）")
            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("確認刪除", key=f"{tab_key}_del_confirm_{tid}", type="primary"):
                    todo_soft_delete(tid, user)
                    del st.session_state[del_key]
                    st.rerun()
            with dc2:
                if st.button("取消", key=f"{tab_key}_del_cancel_{tid}"):
                    del st.session_state[del_key]
                    st.rerun()

        # ── activity log ──
        st.divider()
        st.markdown("**最近活動：**")
        _render_activity(activity_log_list(tid, limit=5))


def render_task_list(tasks: list[dict], tab_key: str) -> None:
    if not tasks:
        st.markdown(
            '<div class="empty-todo">'
            '<div class="empty-todo-icon">📭</div>'
            '<div class="empty-todo-text">沒有符合的任務</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return
    st.caption(f"共 {len(tasks)} 筆")
    for task in tasks:
        _render_task_card(task, tab_key)


# ── page header ───────────────────────────────────────────────────────────────

now = datetime.now()
weekdays = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
today_str = f"{now.month}月{now.day}日，{weekdays[now.weekday()]}"

h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(
        f'<div class="page-title">今日待辦</div>'
        f'<div class="page-subtitle">{today_str} &nbsp;·&nbsp; {user_short}</div>',
        unsafe_allow_html=True,
    )
with h2:
    if st.button("＋ 新增任務", type="primary", use_container_width=True):
        st.session_state["show_add_form"] = not st.session_state.get("show_add_form", False)

# ── add task form ─────────────────────────────────────────────────────────────

if st.session_state.get("show_add_form", False):
    with st.expander("➕ 新增任務", expanded=True):
        with st.form("create_todo", clear_on_submit=True):
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                new_title = st.text_area("標題 *", placeholder="任務名稱（必填）", height=68)
            with cf2:
                new_priority = st.selectbox("優先度", list(PRIORITY_LABEL.values()), index=1)

            new_desc = st.text_area("描述", height=68, placeholder="詳細說明（選填）")

            cf3, cf4 = st.columns(2)
            with cf3:
                new_owner  = st.text_input("負責人", value=user)
                new_status = st.selectbox(
                    "初始狀態", STATUSES,
                    format_func=lambda x: f"{STATUS_ICON[x]} {STATUS_LABEL[x]}",
                )
            with cf4:
                new_deadline_d = st.date_input("截止日期", value=None)
                new_deadline_t = st.selectbox("截止時間", TIME_OPTS, index=16, key="add_dl_t", label_visibility="collapsed")
                new_remind_d   = st.date_input("提醒日期", value=None)
                new_remind_t   = st.selectbox("提醒時間", TIME_OPTS, index=16, key="add_rm_t", label_visibility="collapsed")

            new_tags_raw = st.text_input("標籤", placeholder="逗號分隔，例：採購, 緊急")
            new_private  = st.checkbox("🔒 私人任務（僅自己可見）", value=False)

            sb1, sb2 = st.columns(2)
            with sb1:
                submitted = st.form_submit_button("🚀 建立任務", type="primary", use_container_width=True)
            with sb2:
                cancelled = st.form_submit_button("✕ 取消", use_container_width=True)

            if submitted:
                if not new_title.strip():
                    st.error("標題為必填")
                else:
                    todo_create(
                        title=new_title.strip().replace("\n", " "),
                        description=new_desc.strip(),
                        status=new_status,
                        priority=PRIORITY_INT[new_priority],
                        owner_user=new_owner.strip() or user,
                        created_by=user,
                        deadline_at=_datetime_or_none(new_deadline_d, new_deadline_t),
                        remind_at=_datetime_or_none(new_remind_d, new_remind_t),
                        tag_names=_parse_tags_input(new_tags_raw) or None,
                        is_private=1 if new_private else 0,
                    )
                    st.success("✅ 任務已建立！")
                    st.session_state["show_add_form"] = False
                    st.rerun()
            if cancelled:
                st.session_state["show_add_form"] = False
                st.rerun()

# ── filter bar ────────────────────────────────────────────────────────────────

fc1, fc2, fc3 = st.columns([4, 2, 2])
with fc1:
    keyword = st.text_input("搜尋", placeholder="🔍 搜尋任務…", label_visibility="collapsed")
with fc2:
    sort = st.selectbox(
        "排序", ["updated_desc", "deadline_asc", "priority_asc"],
        format_func=lambda x: {
            "updated_desc": "⏱ 最近更新",
            "deadline_asc": "📅 截止日期",
            "priority_asc": "🔴 優先度",
        }[x],
        label_visibility="collapsed",
    )
with fc3:
    scope = st.radio("範圍", ["全部", "我的"], index=1, horizontal=True, label_visibility="collapsed")

all_tags = [t["name"] for t in tags_list()]
if all_tags:
    tag_filter = st.multiselect(
        "標籤篩選", options=all_tags, placeholder="🏷️ 篩選標籤…",
        label_visibility="collapsed",
    )
else:
    tag_filter = []

mine_user = user if scope == "我的" else ""

# ── load tasks & count ────────────────────────────────────────────────────────

tasks_all = todo_list(
    keyword=keyword,
    tag_names=tag_filter or None,
    mine_user=mine_user,
    include_done=True,
    sort=sort,
    current_user=user,
)
counts = {s: sum(1 for t in tasks_all if t["status"] == s) for s in STATUSES}

# ── status tabs ───────────────────────────────────────────────────────────────

tab_labels = [
    f"全部  {len(tasks_all)}",
    f"⬜ 待辦  {counts['open']}",
    f"▶️ 進行中  {counts['doing']}",
    f"⏸ 封鎖  {counts['blocked']}",
    f"✅ 完成  {counts['done']}",
]
tabs = st.tabs(tab_labels)

with tabs[0]:
    render_task_list(tasks_all, "t0")
with tabs[1]:
    render_task_list([t for t in tasks_all if t["status"] == "open"], "t1")
with tabs[2]:
    render_task_list([t for t in tasks_all if t["status"] == "doing"], "t2")
with tabs[3]:
    render_task_list([t for t in tasks_all if t["status"] == "blocked"], "t3")
with tabs[4]:
    render_task_list([t for t in tasks_all if t["status"] == "done"], "t4")
