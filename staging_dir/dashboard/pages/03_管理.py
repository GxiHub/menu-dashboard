"""03_admin.py — 管理後台 v2.0
功能：系統狀態 / 資料庫備份 / CSV 匯入出 / Promote & Rollback
"""
from __future__ import annotations

import io
import os
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from ui_common import apply_base_css, render_sidebar_admin, load_menu_df_cn, to_en, invalidate_menu_cache
from rbac import require_page, get_user_email, log_access
from app.backup import backup_db, restore_prev
from app.crud import save_df

APP_ENV = os.environ.get("APP_ENV", "prod")

# ── page setup ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="管理｜菜單儀表板", layout="wide")
user = require_page("管理")
apply_base_css()
render_sidebar_admin()

log_access(user, "管理")

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Page-specific overrides only — base styles in ui_common.py */
.block-container { padding-top: 4rem !important; max-width: 900px !important; }
.page-subtitle { margin-bottom: 0.5rem; }

.admin-card { background: white; border-radius: var(--radius-lg, 16px); padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 12px; }
.metric-card { background: white; border-radius: var(--radius-md, 12px); padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.metric-label { font-size: 0.75rem; color: var(--color-text-muted, #9e9e9e); font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
.metric-value { font-size: 1.1rem; font-weight: 800; color: var(--color-text, #1a1a1a); margin-top: 4px; word-break: break-all; }
.metric-sub   { font-size: 0.75rem; color: var(--color-text-muted, #9e9e9e); margin-top: 2px; }

.env-badge { display: inline-block; border-radius: var(--radius-pill, 99px); padding: 2px 12px; font-size: 0.78rem; font-weight: 700; vertical-align: middle; margin-left: 8px; }
.env-staging { background: #fff7ed; color: #ea580c; }
.env-prod    { background: #eff6ff; color: #3b82f6; }

.log-line { font-family: monospace; font-size: 0.76rem; padding: 2px 0; border-bottom: 1px solid #f8f8f8; }

.backup-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; font-size: 0.83rem; }
.backup-row:last-child { border-bottom: none; }
.backup-name { color: #444; font-family: monospace; }
.backup-meta { color: var(--color-text-muted, #9e9e9e); white-space: nowrap; margin-left: 12px; }

@media (max-width: 640px) {
  .block-container { max-width: 100% !important; padding-top: 2rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── header ────────────────────────────────────────────────────────────────────

env_label = "STAGING" if APP_ENV == "staging" else "PROD"
env_cls   = "env-staging" if APP_ENV == "staging" else "env-prod"
st.markdown(
    f'<div class="page-title">管理後台'
    f'<span class="env-badge {env_cls}">{env_label}</span></div>'
    f'<div class="page-subtitle">登入者：{user}</div>',
    unsafe_allow_html=True,
)

# ── helpers ───────────────────────────────────────────────────────────────────

def _read_file(path: str, default: str = "(無記錄)") -> str:
    try:
        return Path(path).read_text(encoding="utf-8").strip() or default
    except Exception:
        return default

def _fmt_size(b: int) -> str:
    if b < 1024:        return f"{b} B"
    if b < 1024 ** 2:   return f"{b/1024:.1f} KB"
    return f"{b/1024/1024:.1f} MB"

def _run(cmd: str, timeout: int = 60) -> tuple[bool, str]:
    try:
        p = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        combined = out + ("\n" + err if err else "")
        return p.returncode == 0, combined
    except subprocess.TimeoutExpired:
        return False, "[TIMEOUT]"
    except Exception as e:
        return False, f"[ERROR] {e}"

def _metric(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return (f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>{sub_html}</div>')

# ── tabs ──────────────────────────────────────────────────────────────────────

t1, t2, t3, t4, t5 = st.tabs([
    "📊 系統狀態",
    "💾 資料庫備份",
    "📄 CSV 匯入／匯出",
    "🚀 Promote / Rollback",
    "👤 登入紀錄",
])

# ════════════════════════════════════════════════════════════════════════
# Tab 1 — 系統狀態
# ════════════════════════════════════════════════════════════════════════

with t1:
    app_ver  = _read_file("/app/VERSION.txt", "—")
    prod_job = _read_file("/home/pi53/dashboard/current/DEPLOYED.txt")
    stag_job = _read_file("/app/DEPLOYED.txt")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(_metric("App 版本", app_ver), unsafe_allow_html=True)
    with c2:
        st.markdown(_metric("PROD 版本", prod_job[:35] + ("…" if len(prod_job) > 35 else "")), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric("Staging 版本", stag_job[:35] + ("…" if len(stag_job) > 35 else "")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Promote log
    st.markdown("**📋 最近部署記錄**")
    log_path = "/home/pi53/dashboard/logs/promote.log"
    try:
        lines = Path(log_path).read_text(encoding="utf-8").strip().splitlines()
        recent = lines[-30:][::-1]
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        rows = ""
        for ln in recent:
            ln_lower = ln.lower()
            color = "#2ea85a" if ("done" in ln_lower or "ok" in ln_lower) else \
                    "#ef4444" if "error" in ln_lower else "#555"
            rows += f'<div class="log-line" style="color:{color}">{ln}</div>'
        st.markdown(rows, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        st.info("尚無部署記錄")

# ════════════════════════════════════════════════════════════════════════
# Tab 2 — 資料庫備份
# ════════════════════════════════════════════════════════════════════════

with t2:
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("💾 立即備份", type="primary", use_container_width=True):
            ok = backup_db("manual_admin")
            st.toast("✅ 備份完成！") if ok else st.toast("❌ 備份失敗", icon="🚨")
            st.rerun()
    with col_b2:
        if st.button("⚠️ 還原上一次備份", use_container_width=True):
            st.session_state["confirm_restore"] = True

    if st.session_state.get("confirm_restore"):
        st.warning("⚠️ 這會以 `menu_prev.db` 覆蓋目前資料庫，確定嗎？")
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("確認還原", type="primary", key="do_restore"):
                ok = restore_prev()
                st.session_state.pop("confirm_restore", None)
                st.success("✅ 已還原！") if ok else st.error("找不到備份 (menu_prev.db)")
                st.rerun()
        with rc2:
            if st.button("取消", key="cancel_restore"):
                st.session_state.pop("confirm_restore", None)
                st.rerun()

    st.divider()

    backup_dir = Path("/app/data/backup")
    try:
        bfiles = sorted(backup_dir.glob("*.db"), key=lambda x: x.stat().st_mtime, reverse=True)
    except Exception:
        bfiles = []

    if not bfiles:
        st.info("尚無備份檔案。點上方「立即備份」建立第一份備份。")
    else:
        st.caption(f"共 {len(bfiles)} 個備份（最新在上）")
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        rows = ""
        for bf in bfiles:
            size  = _fmt_size(bf.stat().st_size)
            mtime = datetime.fromtimestamp(bf.stat().st_mtime).strftime("%m/%d %H:%M")
            icon  = "📌" if bf.name == "menu_prev.db" else "📁"
            rows += (f'<div class="backup-row">'
                     f'<span class="backup-name">{icon} {bf.name}</span>'
                     f'<span class="backup-meta">{size} · {mtime}</span>'
                     f'</div>')
        st.markdown(rows, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# Tab 3 — CSV 匯入／匯出
# ════════════════════════════════════════════════════════════════════════

with t3:
    st.markdown("#### ⬇️ 匯出目前菜單")
    df_export = load_menu_df_cn()
    if df_export.empty:
        st.info("目前沒有資料可匯出。")
    else:
        ts_str    = datetime.now().strftime("%Y%m%d_%H%M")
        csv_bytes = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            f"⬇️ 下載 CSV（{len(df_export)} 筆）",
            data=csv_bytes,
            file_name=f"menu_{ts_str}.csv",
            mime="text/csv",
            type="primary",
        )

    st.divider()

    st.markdown("#### ⬆️ 匯入 CSV")
    st.caption("上傳後可預覽，確認才會覆蓋現有資料，並自動備份。")

    uploaded = st.file_uploader("選擇 CSV 檔", type=["csv"], label_visibility="collapsed")
    if uploaded:
        try:
            df_new = pd.read_csv(uploaded)
            st.success(f"✅ 解析成功：**{len(df_new)} 筆**，{len(df_new.columns)} 個欄位")
            with st.expander("📋 預覽前 10 筆", expanded=True):
                st.dataframe(df_new.head(10), use_container_width=True)

            if st.button("✅ 確認匯入（覆蓋現有資料）", type="primary"):
                backup_db("before_csv_import")
                try:
                    save_df(to_en(df_new))
                except Exception:
                    save_df(df_new)
                invalidate_menu_cache()
                st.toast(f"✅ 已匯入 {len(df_new)} 筆，舊資料已自動備份！")
                st.rerun()
        except Exception as e:
            st.error(f"CSV 解析失敗：{e}")

# ════════════════════════════════════════════════════════════════════════
# Tab 4 — Promote / Rollback
# ════════════════════════════════════════════════════════════════════════

with t4:
    if APP_ENV != "staging":
        st.info(
            "⚠️ Promote / Rollback 只在 **Staging** 環境開放。\n\n"
            "請至 staging.tfooddata.com 的 Admin 頁面操作。"
        )
    else:
        prod_job = _read_file("/home/pi53/dashboard/current/DEPLOYED.txt")
        stag_job = _read_file("/app/DEPLOYED.txt")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(_metric("PROD 目前版本", prod_job, "已上線"), unsafe_allow_html=True)
        with c2:
            st.markdown(_metric("Staging 版本", stag_job, "待 promote"), unsafe_allow_html=True)

        is_same = (prod_job == stag_job)
        if is_same:
            st.info("ℹ️ PROD 與 Staging 版本相同，無需 Promote。")

        st.markdown("<br>", unsafe_allow_html=True)

        col_p, col_r = st.columns(2)

        with col_p:
            st.markdown("**🚀 Promote to PROD**")
            st.caption("把 Staging 版本推上 PROD，自動備份舊 PROD。")
            if st.button("Promote to PROD →", type="primary",
                         use_container_width=True, disabled=is_same, key="page_btn_promote"):
                st.session_state["confirm_promote"] = True

        with col_r:
            st.markdown("**↩️ Rollback PROD**")
            st.caption("回滾 PROD 到上一次 Promote 前的備份版本。")
            if st.button("← Rollback PROD", use_container_width=True, key="page_btn_rollback"):
                st.session_state["confirm_rollback"] = True

        if st.session_state.get("confirm_promote"):
            st.warning(f"⚠️ 確定將 `{stag_job}` 推上 PROD？")
            pc1, pc2 = st.columns(2)
            with pc1:
                if st.button("✅ 確認 Promote", type="primary", key="do_promote"):
                    with st.spinner("Promoting..."):
                        ok, out = _run("python3 /host/promote_ui.py")
                    st.session_state.pop("confirm_promote", None)
                    st.success("✅ Promote 完成！") if ok else st.error("Promote 失敗")
                    st.code(out, language="text")
            with pc2:
                if st.button("取消", key="cancel_promote"):
                    st.session_state.pop("confirm_promote", None)
                    st.rerun()

        if st.session_state.get("confirm_rollback"):
            st.warning("⚠️ 確定回滾 PROD？此操作無法復原。")
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("✅ 確認 Rollback", type="primary", key="do_rollback"):
                    with st.spinner("Rolling back..."):
                        ok, out = _run("python3 /host/rollback_ui.py")
                    st.session_state.pop("confirm_rollback", None)
                    st.success("✅ Rollback 完成！") if ok else st.error("Rollback 失敗")
                    st.code(out, language="text")
            with rc2:
                if st.button("取消", key="cancel_rollback"):
                    st.session_state.pop("confirm_rollback", None)
                    st.rerun()


with t5:
    from rbac import (permission_list, set_user_role, access_log_recent,
                      ROLE_LABEL, ROLE_OPTIONS, ADMIN_EMAIL,
                      get_role_pages, set_role_pages, ALL_PAGES)

    # ── 角色頁面設定 ────────────────────────────────────────────────────────
    with st.expander("⚙️ 角色頁面設定"):
        editable_roles = ["level1", "level2", "level3", "level4", "level5", "level6", "viewer", "editor"]
        page_opts = [pg for pg in ALL_PAGES if pg != "管理"]

        for role in editable_roles:
            st.markdown(f"**{ROLE_LABEL.get(role, role)}**")
            current_pages = get_role_pages(role)
            cols = st.columns(len(page_opts) + 1)

            selected = {}
            for i, pg in enumerate(page_opts):
                with cols[i]:
                    selected[pg] = st.checkbox(
                        pg, value=(pg in current_pages), key=f"rp_{role}_{pg}"
                    )

            with cols[-1]:
                if st.button("儲存", key=f"rp_save_{role}"):
                    new_pages = {pg for pg, v in selected.items() if v}
                    set_role_pages(role, new_pages, user)
                    st.success("✅")
                    st.rerun()

        st.divider()
        st.caption("blocked = 無頁面（固定） ｜ admin = 全部（固定）")

    st.markdown("**帳號權限管理**")
    st.caption("角色：👑 管理員 全頁面 ｜ ✏️ 編輯 顯示/待辦/待辦1/行事曆 ｜ Lv6 +待辦4 ｜ Lv5 +待辦3 ｜ Lv4 +待辦2 ｜ Lv3 +顯示 ｜ Lv2 +行事曆 ｜ Lv1 待辦1 ｜ 👁 訪客 僅顯示 ｜ 🚫 封鎖")
    st.markdown("")

    users = permission_list()
    if not users:
        st.info("尚無登入記錄。使用者進入任一頁面後會自動出現在此。")
    else:
        role_opts = ROLE_OPTIONS

        for u in users:
            email     = u["user_email"]
            cur_role  = u["role"]
            last_seen = (u["last_seen"] or "")[:16].replace("T", " ") or "未登入"
            visits    = u["visit_count"] or 0
            is_admin  = (email == ADMIN_EMAIL)
            skey      = f"role_{email}"

            # 用 session_state 初始化選取值（只在首次渲染時設定，避免 rerun 時 index 覆蓋用戶選取）
            if skey not in st.session_state:
                st.session_state[skey] = cur_role

            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                st.markdown(
                    f'<div style="padding:6px 0">'
                    f'<div style="font-weight:600;font-size:0.9rem">{email}'
                    + (' &nbsp;<span style="background:#fef3c7;color:#92400e;border-radius:99px;padding:1px 8px;font-size:0.7rem">Admin</span>' if is_admin else '')
                    + f'</div>'
                    f'<div style="font-size:0.75rem;color:#aaa">最後登入：{last_seen} &nbsp;·&nbsp; {visits} 次</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                if is_admin:
                    st.markdown(
                        '<div style="padding:10px 0;font-size:0.85rem;color:#92400e">👑 管理員（固定）</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    new_role = st.selectbox(
                        "角色",
                        role_opts,
                        format_func=lambda x: ROLE_LABEL.get(x, x),
                        key=skey,
                        label_visibility="collapsed",
                    )
            with c3:
                if not is_admin:
                    if st.button("儲存", key=f"save_{email}", use_container_width=True):
                        set_user_role(email, new_role, user)
                        st.toast(f"✅ {email.split('@')[0]} 已更新為 {ROLE_LABEL.get(new_role, new_role)}")
                        st.rerun()

            st.divider()

    with st.expander("📋 最近登入記錄（50 筆）"):
        for r in access_log_recent(50):
            ts = r["accessed_at"][:16].replace("T", " ")
            st.caption(f"{ts}　{r['user_email']}　→ {r['page']}")
