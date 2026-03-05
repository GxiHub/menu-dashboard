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

# Flask API base（Docker 內部透過 bridge gateway 連到 host）
API_BASE = "http://172.20.0.1:5005"

# ── 自訂樣式 ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Page-specific: dark-theme post cards */
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
st.caption("輸入社團網址或 ID，自動抓取最新貼文與留言")


# ── 輸入區 ────────────────────────────────────────────────────────────────────
col_url, col_n = st.columns([4, 1])
with col_url:
    group_url = st.text_input(
        "社團網址 / Group ID",
        value="https://www.facebook.com/groups/3238547836318385",
        label_visibility="collapsed",
        placeholder="社團網址 / Group ID / 社團路徑名稱",
    )
with col_n:
    max_posts = st.number_input("篇數", min_value=1, max_value=20, value=5, label_visibility="collapsed")

col_go, col_load, _ = st.columns([1, 1, 3])
with col_go:
    btn_scrape = st.button("開始抓取", type="primary", use_container_width=True)
with col_load:
    btn_load = st.button("載入舊資料", use_container_width=True)


# ── 工具函式 ──────────────────────────────────────────────────────────────────
def render_posts(posts: list, group_name: str = ""):
    """將貼文列表渲染為卡片"""
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
    """檢查 Flask API 是否可連線"""
    try:
        r = requests.get(f"{API_BASE}/api/status", timeout=3)
        return r.ok
    except Exception:
        return False


# ── 開始抓取 ──────────────────────────────────────────────────────────────────
if btn_scrape:
    if not group_url.strip():
        st.warning("請輸入社團網址或 ID")
        st.stop()

    if not api_ok():
        st.error("爬蟲服務未啟動（host:5005 無回應）。請在 Pi 上執行 `python3 ~/fb_scraper/app.py &`")
        st.stop()

    # 發起爬取
    try:
        r = requests.post(
            f"{API_BASE}/api/scrape",
            json={"group_url": group_url.strip(), "max_posts": max_posts},
            timeout=5,
        )
        data = r.json()
        if not data.get("started"):
            st.error(data.get("error", "啟動失敗"))
            st.stop()
    except Exception as e:
        st.error(f"請求失敗：{e}")
        st.stop()

    # 輪詢狀態
    status_area = st.empty()
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
                render_posts(result.get("posts", []), result.get("group_name", ""))
            break
        else:
            # 估算進度
            n_logs = len(logs)
            progress_bar.progress(min(n_logs * 5, 95), text="爬取中...")

# ── 載入舊資料 ────────────────────────────────────────────────────────────────
if btn_load:
    if not api_ok():
        st.error("爬蟲服務未啟動（host:5005 無回應）")
        st.stop()
    try:
        data = requests.get(f"{API_BASE}/api/latest", timeout=5).json()
        posts = data.get("posts", [])
        if posts:
            render_posts(posts, data.get("group_name", "歷史資料"))
        else:
            st.info("沒有舊資料")
    except Exception as e:
        st.error(f"載入失敗：{e}")
