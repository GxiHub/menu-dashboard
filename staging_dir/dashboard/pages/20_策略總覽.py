from rbac import require_page, log_access
import streamlit as st
from pathlib import Path

_PAGE = "策略總覽"
email = require_page(_PAGE)
log_access(email, _PAGE)

# 讀取 HTML 報告
_html_path = Path(__file__).parent.parent / "static" / "txo_report.html"
try:
    html_content = _html_path.read_text(encoding="utf-8")
    # 拿掉 <nav> 的 sticky（避免在 iframe 內撞版）
    html_content = html_content.replace("position: sticky;", "position: relative;")
    st.components.v1.html(html_content, height=4800, scrolling=True)
except FileNotFoundError:
    st.error(f"找不到報告檔案：{_html_path}")
