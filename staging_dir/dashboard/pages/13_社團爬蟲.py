"""社團爬蟲 — 透過 Flask API (host:5005) 抓取 FB 社團貼文"""
import time
import requests
import streamlit as st
from rbac import require_page, log_access
from ui_common import apply_base_css, render_sidebar_admin

user = require_page("社團爬蟲")
log_access(user, "社團爬蟲")
apply_base_css()

with st.sidebar:
    render_sidebar_admin()

API_BASE = "http://172.20.0.1:5005"

# ── 樣式 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.post-card {
    background: #16213e; border-radius: var(--radius-md, 12px); padding: 18px 20px;
    margin-bottom: 14px; border: 1px solid #0f3460;
}
.post-author { font-weight: 700; color: #00d4ff; font-size: 1.05em; }
.post-idx { color: #666; font-size: 0.85em; float: right; }
.post-body { line-height: 1.7; margin: 10px 0; white-space: pre-wrap;
             word-break: break-word; color: #ddd; }
.post-link a { color: #4a90d9; font-size: 0.85em; text-decoration: none; }
.post-link a:hover { text-decoration: underline; }
.comment-box { background: #0f1a35; border-radius: var(--radius-sm, 8px); padding: 10px 14px;
               margin-bottom: 6px; }
.comment-author { font-weight: 600; color: #66b3ff; font-size: 0.9em; margin-bottom: 3px; }
.comment-body { font-size: 0.88em; line-height: 1.5; color: #ccc;
                white-space: pre-wrap; word-break: break-word; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🕷 FB 社團爬蟲")


# ── 工具函式 ──────────────────────────────────────────────────────────────────
def render_posts(posts: list, group_name: str = ""):
    if group_name:
        st.success(f"社團：**{group_name}** — 共 {len(posts)} 篇")
    if not posts:
        st.info("沒有抓到貼文")
        return
    for i, post in enumerate(posts):
        author = post.get("author") or "未知"
        content = post.get("content") or ""
        url = post.get("url") or ""
        comments = post.get("comments") or []

        link_html = f'<div class="post-link"><a href="{url}" target="_blank">🔗 查看原文</a></div>' if url else ""
        st.markdown(
            f'<div class="post-card">'
            f'<span class="post-idx">#{i+1}</span>'
            f'<div class="post-author">{author}</div>'
            f'<div class="post-body">{content}</div>'
            f'{link_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if comments:
            with st.expander(f"💬 {len(comments)} 則留言"):
                for c in comments:
                    st.markdown(
                        f'<div class="comment-box">'
                        f'<div class="comment-author">{c.get("commenter", "匿名")}</div>'
                        f'<div class="comment-body">{c.get("body", "")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


def api_ok() -> bool:
    try:
        return requests.get(f"{API_BASE}/api/status", timeout=3).ok
    except Exception:
        return False


def load_saved_groups():
    try:
        return requests.get(f"{API_BASE}/api/groups", timeout=3).json()
    except Exception:
        return []


# ── 主頁面 Tab ────────────────────────────────────────────────────────────────
tab_search, tab_history, tab_manage = st.tabs(["🔍 搜尋", "📚 歷史記錄", "⚙️ 管理社團"])


# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: 搜尋
# ══════════════════════════════════════════════════════════════════════════════
with tab_search:
    saved_groups = load_saved_groups()

    if not saved_groups:
        st.info("尚未儲存任何社團，請到「管理社團」Tab 新增")
    else:
        # 下拉選單選社團
        group_options = {g["group_name"]: g for g in saved_groups}
        selected_name = st.selectbox(
            "選擇社團",
            list(group_options.keys()),
            key="search_group_select",
        )
        selected_group = group_options[selected_name]

        # 關鍵字 + 篇數
        col_kw, col_n = st.columns([4, 1])
        with col_kw:
            keyword = st.text_input("關鍵字（選填）", placeholder="輸入關鍵字篩選貼文...", key="search_kw")
        with col_n:
            max_posts = st.number_input("篇數", min_value=1, max_value=20, value=5,
                                        label_visibility="collapsed", key="search_n")

        btn_search = st.button("開始搜尋", type="primary", use_container_width=True)

    if saved_groups and btn_search:
        if not api_ok():
            st.error("爬蟲服務未啟動（host:5005 無回應）")
            st.stop()

        try:
            r = requests.post(
                f"{API_BASE}/api/scrape",
                json={
                    "group_url": selected_group["group_url"],
                    "max_posts": max_posts,
                    "keyword": keyword.strip(),
                },
                timeout=5,
            )
            data = r.json()
            if not data.get("started"):
                st.error(data.get("error", "啟動失敗"))
                st.stop()
        except Exception as e:
            st.error(f"請求失敗：{e}")
            st.stop()

        log_area = st.empty()
        progress_bar = st.progress(0, text="爬取中...")

        while True:
            time.sleep(2)
            try:
                s = requests.get(f"{API_BASE}/api/status", timeout=5).json()
            except Exception:
                continue

            logs = s.get("logs", [])
            log_area.code("\n".join(logs[-20:]), language="text")

            if not s.get("running"):
                progress_bar.progress(100, text="完成")
                result = s.get("result")
                if result and result.get("error"):
                    st.error(f"爬取失敗：{result['error']}")
                elif result:
                    all_posts = result.get("posts", [])
                    kw = keyword.strip()
                    if kw:
                        filtered = [p for p in all_posts if kw.lower() in (p.get("content") or "").lower()]
                        st.info(f"共 {len(all_posts)} 篇，關鍵字「{kw}」篩選後 {len(filtered)} 篇")
                        render_posts(filtered, selected_name)
                    else:
                        render_posts(all_posts, selected_name)
                break
            else:
                progress_bar.progress(min(len(logs) * 5, 95), text="爬取中...")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: 歷史記錄
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.caption("瀏覽過去的爬取記錄")

    try:
        history = requests.get(f"{API_BASE}/api/history", timeout=5).json()
    except Exception:
        history = []

    if not history:
        st.info("尚無歷史記錄")
    else:
        # 篩選
        hist_groups = sorted(set(h.get("group_name", "") for h in history if h.get("group_name")))
        col_fg, col_fk = st.columns(2)
        with col_fg:
            fg = st.selectbox("篩選社團", ["全部"] + hist_groups, key="hist_fg")
        with col_fk:
            fk = st.text_input("搜尋", placeholder="篩選關鍵字...", key="hist_fk")

        filtered = history
        if fg != "全部":
            filtered = [h for h in filtered if h.get("group_name") == fg]
        if fk.strip():
            fk_lower = fk.strip().lower()
            filtered = [h for h in filtered
                        if fk_lower in (h.get("group_name") or "").lower()
                        or fk_lower in (h.get("keyword") or "").lower()]

        if not filtered:
            st.info("沒有符合條件的記錄")
        else:
            for h in filtered:
                kw_label = f" | 🔑 {h['keyword']}" if h.get("keyword") else ""
                label = f"📌 {h.get('group_name', '?')} — {h['post_count']} 篇{kw_label}　({h['scraped_at']})"
                with st.expander(label):
                    try:
                        detail = requests.get(f"{API_BASE}/api/history/{h['id']}", timeout=5).json()
                        if detail.get("keyword"):
                            st.caption(f"關鍵字：{detail['keyword']}")
                        render_posts(detail.get("posts", []))
                    except Exception as e:
                        st.error(f"載入失敗：{e}")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: 管理社團
# ══════════════════════════════════════════════════════════════════════════════
with tab_manage:
    st.caption("新增或移除常用社團")

    # 新增社團
    st.markdown("#### 新增社團")
    new_url = st.text_input(
        "社團網址 / Group ID",
        placeholder="https://www.facebook.com/groups/...",
        key="manage_new_url",
    )
    btn_add = st.button("查詢並儲存", type="primary", key="manage_add_btn")

    if btn_add:
        if not new_url.strip():
            st.warning("請輸入社團網址")
        elif not api_ok():
            st.error("爬蟲服務未啟動")
        else:
            with st.spinner("查詢社團名稱中...（約 10-20 秒）"):
                try:
                    r = requests.post(
                        f"{API_BASE}/api/group_info",
                        json={"group_url": new_url.strip()},
                        timeout=60,
                    )
                    info = r.json()
                    if info.get("error"):
                        st.error(f"查詢失敗：{info['error']}")
                    elif info.get("group_name"):
                        # 儲存
                        requests.post(
                            f"{API_BASE}/api/groups",
                            json={"group_url": new_url.strip(), "group_name": info["group_name"]},
                            timeout=5,
                        )
                        st.toast(f"已儲存：{info['group_name']}")
                        st.rerun()
                    else:
                        st.warning("無法取得社團名稱")
                except Exception as e:
                    st.error(f"請求失敗：{e}")

    # 已儲存社團列表
    st.markdown("---")
    st.markdown("#### 已儲存社團")
    saved = load_saved_groups()
    if not saved:
        st.info("尚未儲存任何社團")
    else:
        for g in saved:
            col_name, col_del = st.columns([5, 1])
            with col_name:
                st.markdown(f"**{g['group_name']}**")
                st.caption(g["group_url"])
            with col_del:
                if st.button("刪除", key=f"del_group_{g['id']}"):
                    requests.delete(f"{API_BASE}/api/groups/{g['id']}", timeout=5)
                    st.toast(f"已刪除：{g['group_name']}")
                    st.rerun()
