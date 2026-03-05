from pathlib import Path
from datetime import datetime
import streamlit as st
from rbac import require_page, log_access
from ui_common import render_sidebar_admin

user = require_page("簡報")
log_access(user, "簡報")

SLIDES_DIR = Path(__file__).parent.parent / "slides"
NOTES_DIR  = Path("/app/data/slides_notes")
NOTES_DIR.mkdir(exist_ok=True)

def get_title(path: Path) -> str:
    name = path.stem
    parts = name.split("_", 1)
    return parts[1] if len(parts) > 1 else name

def notes_path(slide: Path) -> Path:
    return NOTES_DIR / (slide.stem + ".notes.md")

slides = sorted(s for s in SLIDES_DIR.glob("*.md") if not s.name.endswith(".notes.md"))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_admin()
    if slides:
        st.markdown("---")
        st.markdown("### 📊 簡報清單")
        titles = [get_title(s) for s in slides]
        selected_idx = st.radio(
            "", range(len(titles)),
            format_func=lambda i: titles[i],
            label_visibility="collapsed"
        )
    else:
        selected_idx = None

if not slides:
    st.info("尚無簡報。請在 slides/ 資料夾新增 .md 檔案。")
    st.stop()

# ── 主要內容 ──────────────────────────────────────────────────────────────────
selected = slides[selected_idx]
np = notes_path(selected)

content = selected.read_text(encoding="utf-8")
st.markdown(content, unsafe_allow_html=True)

# ── 筆記格 ────────────────────────────────────────────────────────────────────
st.divider()

existing_notes = np.read_text(encoding="utf-8").strip() if np.exists() else ""

with st.expander("📝 我的筆記（供下次更新簡報時使用）", expanded=bool(existing_notes)):
    if existing_notes:
        st.markdown(
            f'<div style="background:#f8f9fa;border-radius:8px;padding:12px 16px;'
            f'font-size:0.85rem;color:#555;white-space:pre-wrap;margin-bottom:12px">'
            f'{existing_notes}</div>',
            unsafe_allow_html=True
        )
        if st.button("🗑 清除所有筆記", key="clear_notes"):
            np.write_text("", encoding="utf-8")
            st.success("已清除")
            st.rerun()
        st.markdown("---")

    new_note = st.text_area(
        "新增筆記",
        placeholder="輸入補充資訊、修正內容、新發現…\n儲存後告訴我「更新簡報」，我會自動讀取並合併重寫。",
        height=120,
        label_visibility="collapsed",
        key=f"note_input_{selected.stem}"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💾 儲存筆記", type="primary", use_container_width=True):
            if new_note.strip():
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                entry = f"[{ts}] {user}\n{new_note.strip()}\n\n"
                with open(np, "a", encoding="utf-8") as f:
                    f.write(entry)
                st.success("✅ 已儲存")
                st.rerun()
            else:
                st.warning("請輸入內容再儲存")
    with col2:
        if existing_notes:
            st.caption(f"💡 已有筆記等待合併，告訴我「更新簡報：{get_title(selected)}」即可")
        else:
            st.caption("💡 儲存筆記後告訴我「更新簡報」，我會自動讀取合併重寫")
