import streamlit as st
from ui_common import apply_base_css
from rbac import get_user_email, get_user_role, get_role_pages, init_permission_tables

st.set_page_config(page_title="菜單營運儀表板", layout="wide")
apply_base_css()

init_permission_tables()
_email   = get_user_email()
_role    = get_user_role(_email)
_allowed = get_role_pages(_role)

_PAGE_DEFS = {
    "菜單系統": [
        ("顯示",     "pages/01_顯示.py",     "👀"),
        ("待辦",     "pages/04_待辦.py",     "📋"),
        ("待辦1",    "pages/06_待辦1.py",    "📌"),
        ("待辦2",    "pages/07_待辦2.py",    "📌"),
        ("待辦3",    "pages/08_待辦3.py",    "📌"),
        ("待辦4",    "pages/09_待辦4.py",    "📌"),
        ("待辦5",    "pages/11_待辦5.py",    "📌"),
        ("行事曆",   "pages/05_行事曆.py",   "📅"),
        ("日常表",   "pages/10_日常表.py",   "🗓"),
        ("簡報",     "pages/12_簡報.py",     "📊"),
        ("社團爬蟲", "pages/13_社團爬蟲.py", "🕷"),
        ("管理",     "pages/03_管理.py",     "⚙️"),
    ],
    "策略分析": [
        ("策略總覽",      "pages/20_策略總覽.py",      "📈"),
        ("TXO Theta引擎", "pages/21_TXO_Theta引擎.py", "⚡"),
    ],
}

nav_dict = {}
for section, defs in _PAGE_DEFS.items():
    section_pages = [
        st.Page(path, title=name, icon=icon)
        for name, path, icon in defs
        if name in _allowed
    ]
    if section_pages:
        nav_dict[section] = section_pages

if not nav_dict:
    st.error("您目前沒有任何頁面的訪問權限，請聯絡管理員。")
    st.stop()

pages = st.navigation(nav_dict)
pages.run()
