"""10_日常表.py — 半小時日常時間表（刷子模式 UI）"""
from __future__ import annotations
from datetime import date
import datetime as _dt

import streamlit as st

from ui_common import apply_base_css, render_sidebar_admin
from rbac import require_page, log_access
from app.daily_db import (
    init_daily_tables, get_tags, get_tags_with_id,
    add_tag, delete_tag, get_schedule, save_slot, SLEEP_SLOTS,
)

# ── Page setup ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="日常表｜菜單儀表板", layout="centered")
apply_base_css()
render_sidebar_admin()
init_daily_tables()

user = require_page("日常表")
log_access(user, "日常表")
user_short = user.split("@")[0]

# ── Constants ───────────────────────────────────────────────────────────────────
_EMPTY  = "（空白）"
_CUSTOM = "✏️ 自行填寫"
_CLEAR  = "🧹 清除"

PERIODS = [
    ("🌙 深夜",  range(0, 6)),
    ("🌅 清晨",  range(6, 9)),
    ("☀️ 上午",  range(9, 12)),
    ("🌞 午間",  range(12, 14)),
    ("🌤️ 下午", range(14, 18)),
    ("🌆 傍晚",  range(18, 20)),
    ("🌙 晚上",  range(20, 23)),
    ("🌛 深夜",  range(23, 24)),
]

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ══ 基礎 ══ */
.stApp { background-color: #f0f2f5 !important; }
html, body, .stApp { overflow-x: hidden !important; max-width: 100vw !important; }

/* ── 容器 padding ── */
.stApp > [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > [data-testid="stMain"],
section[data-testid="stMain"],
section[data-testid="stMain"] > div[data-testid="stMainBlockContainer"] {
    padding-left: 0 !important; padding-right: 0 !important;
    max-width: 100% !important; box-sizing: border-box !important;
}
.block-container,
.appview-container .main .block-container {
    padding-top: 2rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    max-width: 580px !important;
    box-sizing: border-box !important;
    width: 100% !important;
}

/* ── 裝飾 ── */
.page-title    { font-size: 1.55rem; font-weight: 800; color: #1a1a1a; margin: 0; }
.page-subtitle { font-size: 0.82rem; color: #9e9e9e; margin-top: 2px; }
button[kind="primary"] {
    background-color: #3dba6e !important; border-color: #3dba6e !important;
    border-radius: 10px !important; font-weight: 700 !important;
}
.stDateInput > div > div > input { border-radius: 10px !important; }
hr { border-color: #e8e8e8 !important; margin: 8px 0 !important; }

/* ── 時段標題 ── */
.period-label {
    font-size: 0.78rem; font-weight: 700; color: #999; letter-spacing: 0.04em;
    padding: 12px 0 4px 2px; margin: 0;
}

/* ── Slot grid ── */
.slot-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
}
.slot-btn {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border-radius: 10px; padding: 8px 4px; text-align: center;
    min-height: 52px; cursor: pointer; transition: all 0.15s;
    border: 1.5px solid #e8e8e8; background: white;
}
.slot-btn:active { transform: scale(0.96); }
.slot-btn .slot-time { font-size: 0.75rem; font-weight: 700; color: #666; }
.slot-btn .slot-val  { font-size: 0.82rem; color: #333; margin-top: 2px;
                       overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
                       max-width: 100%; }
/* 狀態 */
.slot-btn.filled { background: #e8f5e9; border-color: #a5d6a7; }
.slot-btn.sleep  { background: #f3f3f3; border-color: #e0e0e0; opacity: 0.65; }
.slot-btn.sleep .slot-val { color: #aaa; }
.slot-btn.empty  { background: white; border-color: #e8e8e8; }
.slot-btn.empty .slot-val { color: #ccc; font-size: 0.75rem; }

/* ── 自填輸入框 ── */
.stTextInput [data-testid="stWidgetLabel"] { display: none !important; }
.stTextInput > div > div > input {
    border-radius: 10px !important; border-color: #ddd !important;
    font-size: 1rem !important; background: white !important;
}

/* ══ RWD ══ */
@media (max-width: 360px) {
    .slot-grid { grid-template-columns: repeat(2, 1fr); }
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
}
@media (min-width: 500px) {
    .slot-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ── Page header ──────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="page-title">🗓 日常表</div>'
    f'<div class="page-subtitle">{user_short}</div>',
    unsafe_allow_html=True,
)
st.markdown("")

# ── Date picker ──────────────────────────────────────────────────────────────────
today    = date.today()
sel_date = st.date_input("日期", value=today, label_visibility="collapsed")
date_str = str(sel_date)

# 換日期時清除 slot session state
_cache_key = f"_daily_loaded_{user}"
if st.session_state.get(_cache_key) != date_str:
    st.session_state.pop("_brush", None)
    st.session_state[_cache_key] = date_str

# ── Load data ────────────────────────────────────────────────────────────────────
tags     = get_tags()
schedule = get_schedule(date_str, user)

# ── Brush selector (pills) ───────────────────────────────────────────────────────
st.markdown("---")
brush_options = tags + [_CUSTOM, _CLEAR]

brush = st.pills(
    "選擇活動　👆 再點下方時段填入",
    options=brush_options,
    key="_brush",
)

# Custom text input (only when brush is custom)
custom_text = ""
if brush == _CUSTOM:
    custom_text = st.text_input(
        "custom_brush",
        label_visibility="collapsed",
        placeholder="輸入自訂活動…",
        key="_brush_custom_text",
    )

st.markdown("---")

# ── Slot click handler ───────────────────────────────────────────────────────────
def _apply_brush(slot: str) -> None:
    """Apply current brush to a slot and save."""
    if brush is None:
        return
    if brush == _CLEAR:
        save_slot(date_str, slot, "", user)
    elif brush == _CUSTOM:
        txt = st.session_state.get("_brush_custom_text", "")
        if txt.strip():
            save_slot(date_str, slot, txt.strip(), user)
    else:
        save_slot(date_str, slot, brush, user)


# ── Render slot grid ─────────────────────────────────────────────────────────────
for period_name, hours in PERIODS:
    slots = [f"{h:02d}:{m:02d}" for h in hours for m in (0, 30)]

    st.markdown(f'<div class="period-label">{period_name}</div>', unsafe_allow_html=True)

    # Build grid with st.columns (3 per row)
    cols_per_row = 3
    for row_start in range(0, len(slots), cols_per_row):
        row_slots = slots[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, slot in enumerate(row_slots):
            val = schedule.get(slot, "")
            with cols[i]:
                # Determine display
                if val == "睡眠":
                    label = "💤 睡眠"
                    btn_type = "secondary"
                elif val:
                    label = val
                    btn_type = "primary"
                else:
                    label = "─"
                    btn_type = "secondary"

                display = f"{slot}\n{label}"
                if st.button(
                    display,
                    key=f"slot_{slot}",
                    use_container_width=True,
                    type=btn_type,
                    disabled=(brush is None),
                ):
                    _apply_brush(slot)
                    st.rerun()

st.divider()

# ── Tag management ───────────────────────────────────────────────────────────────
with st.expander("🏷️ 標籤管理"):
    with st.form("add_tag_form", clear_on_submit=True):
        ci, cb = st.columns([4, 1])
        with ci:
            new_tag_name = st.text_input("", placeholder="新增標籤名稱…", label_visibility="collapsed")
        with cb:
            submitted = st.form_submit_button("＋", type="primary", use_container_width=True)
        if submitted and new_tag_name.strip():
            ok = add_tag(new_tag_name.strip(), user)
            if ok:
                st.success(f"✅ 已新增「{new_tag_name.strip()}」")
                st.rerun()
            else:
                st.error("⚠️ 標籤已存在")

    st.markdown("**現有標籤**")
    for t in get_tags_with_id():
        r1, r2 = st.columns([5, 1])
        with r1:
            st.write(t["name"])
        with r2:
            if t["name"] != "睡眠":
                if st.button("✕", key=f"del_tag_{t['id']}", use_container_width=True):
                    delete_tag(t["id"])
                    st.rerun()
