"""05_calendar.py — 行事曆 / Rolling Group Availability (Mobile-first)"""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from ui_common import apply_base_css, render_sidebar_admin
from rbac import require_page, log_access
from app.rolling_db import (
    init_rolling_tables,
    group_create, group_get, group_list_for_user, group_list_joinable, group_update, group_archive,
    member_add, member_remove, member_list, is_owner,
    availability_upsert, availability_matrix, intersection_compute, availability_who_yes,
    SLOTS, SLOT_LABEL, STATE_ICON, STATE_CYCLE_MAYBE, STATE_CYCLE_PLAIN,
)

# ── Page setup ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="行事曆｜菜單儀表板", layout="wide")
apply_base_css()
render_sidebar_admin()
init_rolling_tables()

user = require_page("行事曆")
log_access(user, "行事曆")
if not user:
    st.error("Authentication required via Cloudflare Access.")
    st.stop()

user_short = user.split("@")[0]

# ── CSS (mobile-first, iPhone style) ───────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #f0f2f5 !important; }
.block-container { padding-top: 2.5rem !important; max-width: 540px !important;
                   padding-left: 1rem !important; padding-right: 1rem !important; }

/* Page header */
.page-title    { font-size: 1.55rem; font-weight: 800; color: #1a1a1a; margin: 0; }
.page-subtitle { font-size: 0.82rem; color: #9e9e9e; margin-top: 2px; }

/* Group header pill */
.group-pill {
    background: white; border-radius: 14px; padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 0.8rem;
}
.group-name  { font-size: 1.1rem; font-weight: 700; color: #1a1a1a; }
.group-meta  { font-size: 0.76rem; color: #999; margin-top: 3px; line-height: 1.5; }

/* Day card */
.day-card {
    background: white; border-radius: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin-bottom: 10px; overflow: hidden;
}
.day-card-header {
    padding: 10px 16px 6px 16px;
    display: flex; align-items: center; justify-content: space-between;
}
.day-date   { font-size: 1.0rem; font-weight: 700; color: #1a1a1a; }
.day-wd     { font-size: 0.78rem; color: #aaa; margin-left: 6px; }
.day-today  { background: #3dba6e; color: white; border-radius: 99px;
              padding: 1px 9px; font-size: 0.7rem; font-weight: 700; }
.day-card-slots { padding: 4px 12px 12px 12px; }

/* Slot toggle buttons */
.stButton > button {
    border-radius: 12px !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: 10px 4px !important;
    width: 100% !important;
    min-height: 52px !important;
    transition: transform 0.08s, box-shadow 0.08s !important;
    border: 1.5px solid #e8e8e8 !important;
}
.stButton > button:active  { transform: scale(0.95) !important; }

/* YES state = green tint */
[data-btn-state="YES"] > button {
    background: #e8f5ee !important; border-color: #3dba6e !important; color: #2ea85a !important;
}
/* MAYBE state = amber tint */
[data-btn-state="MAYBE"] > button {
    background: #fffbeb !important; border-color: #f59e0b !important; color: #b45309 !important;
}

/* Intersection day card */
.inter-day-card {
    background: white; border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 10px; padding: 12px 16px;
}
.inter-slot-row { display: flex; align-items: center; justify-content: space-between;
                  padding: 5px 0; border-bottom: 1px solid #f3f3f3; }
.inter-slot-row:last-child { border-bottom: none; }
.inter-slot-name  { font-size: 0.88rem; color: #555; font-weight: 500; }
.inter-count      { font-size: 0.88rem; font-weight: 700; color: #1a1a1a; }
.ic-perfect   { color: #2ea85a !important; }
.ic-threshold { color: #3b82f6 !important; }
.ic-empty     { color: #ccc !important; }
.recommend-badge {
    background: #e8f5ee; color: #2ea85a; border-radius: 99px;
    font-size: 0.68rem; font-weight: 700; padding: 2px 8px; margin-left: 6px;
}

/* Top candidate card */
.top-card {
    background: white; border-radius: 14px; padding: 14px 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07); margin-bottom: 10px;
}
.top-card-title { font-size: 0.95rem; font-weight: 700; color: #1a1a1a;
                  display:flex; align-items:center; gap:6px; margin-bottom:10px; }
.top-card-bottom { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
.top-card-count { font-size: 0.88rem; font-weight: 700; color: #2ea85a;
                  background:#e8f5ee; border-radius:99px; padding:3px 10px; }
.rank-badge { background:#f0f2f5; color:#888; border-radius:99px;
              padding:2px 9px; font-size:0.72rem; font-weight:700; }

/* Member row */
.member-row {
    background: white; border-radius: 12px; padding: 11px 14px;
    margin-bottom: 7px; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    display: flex; align-items: center; justify-content: space-between;
}
.member-info { font-size: 0.88rem; color: #333; }
.member-role { font-size: 0.72rem; color: #aaa; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important; border-bottom: 2px solid #e8e8e8 !important;
    background: transparent !important; padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important; padding: 7px 14px !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    color: #9e9e9e !important; background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #2ea85a !important; background: white !important;
    border-bottom: 2px solid #3dba6e !important; font-weight: 700 !important;
}
/* primary green */
button[kind="primary"] {
    background-color: #3dba6e !important; border-color: #3dba6e !important;
    border-radius: 12px !important; font-weight: 700 !important;
}
button[kind="primary"]:hover { background-color: #34a862 !important; }

/* Form inputs */
.stTextInput > div > div > input {
    border-radius: 10px !important; border-color: #e8e8e8 !important; font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus { border-color: #3dba6e !important; }
.stSelectbox > div > div { border-radius: 10px !important; }
.stTextArea textarea { border-radius: 10px !important; border-color: #e8e8e8 !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ─────────────────────────────────────────────────────────────────────
WEEKDAY_ZH = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
_AVATAR_COLORS = [
    "#4F46E5","#0EA5E9","#10B981","#F59E0B",
    "#EF4444","#8B5CF6","#EC4899","#14B8A6",
]

def _avatar_html(members: list[dict], size: int = 22) -> str:
    html = ""
    for m in members:
        email = m["user_email"]
        letter = (m["display_name"] or email)[0].upper()
        color = _AVATAR_COLORS[sum(ord(c) for c in email) % len(_AVATAR_COLORS)]
        title = m["display_name"] or email
        s = str(size)
        fs = str(size // 2 + 1)
        html += (
            f'<span title="{title}" style=' +
            f'"display:inline-flex;align-items:center;justify-content:center;' +
            f'width:{s}px;height:{s}px;border-radius:50%;' +
            f'background:{color};color:white;font-size:{fs}px;' +
            f'font-weight:700;margin:0 2px;flex-shrink:0;">' +
            f'{letter}</span>'
        )
    return html


def rolling_window(offset: int = 0) -> list[date]:
    start = date.today() + timedelta(weeks=offset)
    return [start + timedelta(days=i) for i in range(7)]

def fmt_date(d: date) -> str:
    return f"{d.month}/{d.day}"

def fmt_wd(d: date) -> str:
    return WEEKDAY_ZH[d.weekday()]

def fmt_window(dates: list[date]) -> str:
    return f"{dates[0].strftime('%m/%d')} – {dates[-1].strftime('%m/%d')}"

# ── Page header ──────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="page-title">行事曆</div>'
    f'<div class="page-subtitle">{user_short}</div>',
    unsafe_allow_html=True,
)
st.markdown("")

# ── Load groups ──────────────────────────────────────────────────────────────────
groups = group_list_for_user(user)

if not groups:
    joinable = group_list_joinable(user)
    if joinable:
        st.markdown("**可加入的群組**")
        for jg in joinable:
            jc1, jc2 = st.columns([4, 1])
            with jc1:
                owner_short = jg["owner_email"].split("@")[0]
                desc_txt = f' — {jg["description"]}' if jg.get("description") else ""
                st.markdown(
                    f'<div class="group-pill" style="margin-bottom:6px">'
                    f'<div class="group-name">{jg["name"]}</div>'
                    f'<div class="group-meta">建立者：{owner_short}{desc_txt}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with jc2:
                if st.button("加入", key=f"join_{jg['id']}", type="primary", use_container_width=True):
                    member_add(jg["id"], user, user.split("@")[0])
                    st.success(f"✅ 已加入「{jg['name']}」")
                    st.rerun()
        st.divider()

    st.markdown("**或建立新群組**")
    with st.form("create_group_first"):
        g_name = st.text_input("群組名稱 *", placeholder="例：週末聚餐團")
        g_desc = st.text_input("說明（選填）")
        g_mode = st.selectbox(
            "判定模式",
            ["ALL", "THRESHOLD"],
            format_func=lambda x: "ALL — 全員到才標記" if x == "ALL" else "THRESHOLD — N 人以上標記",
        )
        g_threshold = None
        if g_mode == "THRESHOLD":
            g_threshold = st.number_input("門檻人數 N", min_value=1, value=2, step=1)
        g_maybe = st.checkbox("允許「也許」狀態 🔶")
        if st.form_submit_button("🚀 建立群組", type="primary", use_container_width=True):
            if not g_name.strip():
                st.error("名稱必填")
            else:
                group_create(
                    name=g_name.strip(), description=g_desc.strip(),
                    owner_email=user, allow_maybe=g_maybe,
                    mode=g_mode, threshold_n=int(g_threshold) if g_threshold else None,
                )
                st.success(f"✅ 群組「{g_name.strip()}」已建立！")
                st.rerun()
    st.stop()

# ── Group selector ────────────────────────────────────────────────────────────────
if len(groups) > 1:
    gid_map = {g["name"]: g["id"] for g in groups}
    sel_name = st.selectbox("群組", list(gid_map.keys()), label_visibility="collapsed")
    selected_group_id = gid_map[sel_name]
else:
    selected_group_id = groups[0]["id"]

grp          = group_get(selected_group_id)
members      = member_list(selected_group_id)
total_members = len(members)
user_is_owner = is_owner(selected_group_id, user)
allow_maybe   = bool(grp["allow_maybe"])
week_offset   = st.session_state.get("week_offset", 0)
window_dates  = rolling_window(week_offset)
window_strs   = [str(d) for d in window_dates]
today         = date.today()

# ── Group header ──────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="group-pill">'
    f'<div class="group-name">{grp["name"]}</div>'
    f'<div class="group-meta">'
    f'👥 {total_members} 人 &nbsp;·&nbsp; 📅 {fmt_window(window_dates)}'
    f'{"&nbsp;·&nbsp; 🔶 也許" if allow_maybe else ""}'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Week navigation ─────────────────────────────────────────────────────────────
_wc1, _wc2, _wc3 = st.columns([2, 3, 2])
with _wc1:
    if st.button("← 上週", use_container_width=True):
        st.session_state["week_offset"] = week_offset - 1
        st.rerun()
with _wc2:
    if week_offset == 0:
        st.markdown('<div style="text-align:center;font-size:0.82rem;color:#aaa;padding:6px 0">本週</div>', unsafe_allow_html=True)
    else:
        lbl = f"+{week_offset}週" if week_offset > 0 else f"{week_offset}週"
        if st.button(f"↩ 回本週（{lbl}）", use_container_width=True):
            st.session_state["week_offset"] = 0
            st.rerun()
with _wc3:
    if st.button("下週 →", use_container_width=True):
        st.session_state["week_offset"] = week_offset + 1
        st.rerun()
st.markdown("")

# ── Tabs ──────────────────────────────────────────────────────────────────────────
tab_my, tab_intersect, tab_members = st.tabs([
    "📅 可用性",
    "📊 交集",
    "👥 成員" + (" ✏️" if user_is_owner else ""),
])

# ═══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — My Availability (iPhone Day Cards)
# ═══════════════════════════════════════════════════════════════════════════════════
with tab_my:
    matrix = availability_matrix(selected_group_id, user, window_strs)
    state_cycle = STATE_CYCLE_MAYBE if allow_maybe else STATE_CYCLE_PLAIN

    hint = "✅ 有空 → 🔶 也許 → ⬜ 不行" if allow_maybe else "✅ 有空 → ⬜ 不行"
    st.caption(f"點擊切換：{hint}")
    st.markdown("")

    for d, d_str in zip(window_dates, window_strs):
        is_today = (d == today)
        today_badge = '<span class="day-today">今天</span>' if is_today else ""

        st.markdown(
            f'<div class="day-card">'
            f'<div class="day-card-header">'
            f'<div><span class="day-date">{fmt_date(d)}</span>'
            f'<span class="day-wd">{fmt_wd(d)}</span></div>'
            f'{today_badge}'
            f'</div>'
            f'<div class="day-card-slots">',
            unsafe_allow_html=True,
        )

        slot_cols = st.columns(3)
        for i, slot in enumerate(SLOTS):
            with slot_cols[i]:
                cur = matrix.get((d_str, slot), "NO")
                icon = STATE_ICON[cur]
                label = f"{icon}\n{SLOT_LABEL[slot]}"
                if st.button(label, key=f"av_{d_str}_{slot}", use_container_width=True):
                    nxt = state_cycle[cur]
                    availability_upsert(selected_group_id, user, d_str, slot, nxt)
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Group Intersection
# ═══════════════════════════════════════════════════════════════════════════════════
with tab_intersect:
    intersect   = intersection_compute(selected_group_id, window_strs)
    who_yes     = availability_who_yes(selected_group_id, window_strs)
    mode        = grp["mode"]
    threshold_n = grp["threshold_n"] or total_members

    # Top 3 candidates
    scored = sorted(
        intersect.items(),
        key=lambda kv: kv[1]["yes_count"],
        reverse=True,
    )
    top3 = [(k, v) for k, v in scored if v["yes_count"] > 0][:3]

    if top3:
        st.markdown("**🏆 最佳候選時段**")
        for rank, ((d_str, slot), info) in enumerate(top3, 1):
            d_obj = date.fromisoformat(d_str)
            yes = info["yes_count"]
            total = info["total_members"]
            is_rec = (mode == "ALL" and yes == total) or (mode == "THRESHOLD" and yes >= threshold_n)
            rec_html = '<span class="recommend-badge">推薦</span>' if is_rec else ""
            _av = _avatar_html(who_yes.get((d_str, slot), []), size=26)
            st.markdown(
                f'<div class="top-card">'
                f'<div class="top-card-title">'
                f'<span class="rank-badge">#{rank}</span>'
                f'{fmt_date(d_obj)} {fmt_wd(d_obj)} '
                f'<strong>{SLOT_LABEL[slot]}</strong>'
                f'{rec_html}</div>'
                f'<div class="top-card-bottom">'
                f'{_av}'
                f'<span class="top-card-count">✅ {yes} / {total}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("")

    st.markdown("**📋 每日詳情**")
    for d, d_str in zip(window_dates, window_strs):
        is_today = (d == today)
        today_badge = '<span class="day-today">今天</span>' if is_today else ""
        rows_html = ""
        for slot in SLOTS:
            info = intersect.get((d_str, slot), {"yes_count": 0, "total_members": total_members})
            yes = info["yes_count"]
            tot = info["total_members"]
            _who = who_yes.get((d_str, slot), [])
            _av2 = _avatar_html(_who)
            if yes == 0:
                cnt_cls = "ic-empty"
                cnt_txt = f"— / {tot}"
                rec = ""
            elif (mode == "ALL" and yes == tot) or (mode == "THRESHOLD" and yes >= threshold_n):
                cnt_cls = "ic-perfect"
                cnt_txt = f"✅ {yes}/{tot}"
                rec = '<span class="recommend-badge">推薦</span>'
            else:
                cnt_cls = "ic-normal"
                cnt_txt = f"{yes}/{tot}"
                rec = ""
            rows_html += (
                f'<div class="inter-slot-row">'
                f'<span class="inter-slot-name">{SLOT_LABEL[slot]}</span>'
                f'<span style="display:flex;align-items:center;gap:3px">'
                f'{rec}{_av2}'
                f'<span class="inter-count {cnt_cls}">{cnt_txt}</span>'
                f'</span>'
                f'</div>'
            )
        st.markdown(
            f'<div class="inter-day-card">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">'
            f'<strong>{fmt_date(d)} {fmt_wd(d)}</strong>{today_badge}'
            f'</div>{rows_html}</div>',
            unsafe_allow_html=True,
        )

    legend = "✅ = 全員到齊" if mode == "ALL" else f"✅ = ≥{threshold_n} 人到"
    st.caption(f"判定：{mode} · {legend}")

# ═══════════════════════════════════════════════════════════════════════════════════
# TAB 3 — Member Management
# ═══════════════════════════════════════════════════════════════════════════════════
with tab_members:
    for m in members:
        role_icon = "👑" if m["role"] == "OWNER" else "👤"
        col_info, col_del = st.columns([4, 1])
        with col_info:
            st.markdown(
                f'<div class="member-row">'
                f'<div><div class="member-info">{role_icon} <strong>{m["display_name"]}</strong></div>'
                f'<div class="member-role">{m["user_email"]}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_del:
            if user_is_owner and m["user_email"] != user:
                dk = f"dm_{m['id']}"
                if not st.session_state.get(dk):
                    if st.button("移除", key=f"dmbtn_{m['id']}"):
                        st.session_state[dk] = True
                        st.rerun()
                else:
                    if st.button("確認", key=f"dmok_{m['id']}", type="primary"):
                        member_remove(selected_group_id, m["user_email"])
                        del st.session_state[dk]
                        st.rerun()

    if user_is_owner:
        st.divider()
        st.markdown("**邀請成員**")
        with st.form("add_member"):
            inv_email = st.text_input("Email", placeholder="example@gmail.com")
            inv_name  = st.text_input("顯示名稱（選填）")
            if st.form_submit_button("➕ 邀請", type="primary", use_container_width=True):
                ne = inv_email.strip().lower()
                if not ne or "@" not in ne:
                    st.error("請輸入有效 Email")
                else:
                    member_add(selected_group_id, ne, inv_name.strip())
                    st.success(f"✅ 已邀請 {ne}")
                    st.rerun()

        st.divider()
        with st.expander("⚙️ 群組設定"):
            with st.form("grp_settings"):
                sn   = st.text_input("名稱", value=grp["name"])
                sd   = st.text_input("說明", value=grp["description"] or "")
                sm   = st.selectbox("判定模式", ["ALL", "THRESHOLD"],
                                    index=0 if grp["mode"] == "ALL" else 1,
                                    format_func=lambda x: "ALL" if x == "ALL" else "THRESHOLD")
                st_h = None
                if sm == "THRESHOLD":
                    st_h = st.number_input("門檻 N", min_value=1,
                                           value=grp["threshold_n"] or 2, step=1)
                smb  = st.checkbox("允許也許", value=allow_maybe)
                if st.form_submit_button("💾 儲存", type="primary", use_container_width=True):
                    group_update(selected_group_id,
                                 name=sn.strip(), description=sd.strip(), mode=sm,
                                 threshold_n=int(st_h) if st_h else None,
                                 allow_maybe=1 if smb else 0)
                    st.success("✅ 已儲存")
                    st.rerun()

        with st.expander("⚠️ 封存群組"):
            st.warning("封存後此群組將隱藏，資料保留。")
            arc_confirm = st.text_input("輸入群組名稱確認")
            if st.button("封存", type="primary", use_container_width=True):
                if arc_confirm.strip() == grp["name"]:
                    group_archive(selected_group_id)
                    st.success("已封存")
                    st.rerun()
                else:
                    st.error("名稱不符")

        st.divider()
        with st.expander("➕ 建立另一個群組"):
            with st.form("new_grp"):
                nn = st.text_input("名稱 *")
                nd = st.text_input("說明")
                nm = st.selectbox("模式", ["ALL", "THRESHOLD"],
                                  format_func=lambda x: "ALL" if x == "ALL" else "THRESHOLD")
                nt = None
                if nm == "THRESHOLD":
                    nt = st.number_input("門檻 N", min_value=1, value=2, step=1, key="nt2")
                nmb = st.checkbox("允許也許", key="nmb2")
                if st.form_submit_button("建立", type="primary", use_container_width=True):
                    if not nn.strip():
                        st.error("名稱必填")
                    else:
                        group_create(name=nn.strip(), description=nd.strip(),
                                     owner_email=user, allow_maybe=nmb, mode=nm,
                                     threshold_n=int(nt) if nt else None)
                        st.success("✅ 已建立")
                        st.rerun()

        _joinable = group_list_joinable(user)
        if _joinable:
            with st.expander(f"🔍 加入其他群組（{len(_joinable)} 個可加入）"):
                for jg in _joinable:
                    jc1, jc2 = st.columns([4, 1])
                    with jc1:
                        owner_s = jg["owner_email"].split("@")[0]
                        st.markdown(f"**{jg['name']}** — {owner_s}")
                    with jc2:
                        if st.button("加入", key=f"join2_{jg['id']}", type="primary", use_container_width=True):
                            member_add(jg["id"], user, user.split("@")[0])
                            st.success(f"✅ 已加入「{jg['name']}」")
                            st.rerun()
    else:
        st.caption("只有 Owner 可以管理成員。")
