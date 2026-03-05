from rbac import require_page, log_access
import math
from pathlib import Path

import streamlit as st

from ui_common import apply_base_css, load_menu_df_cn, add_margin_cols, keyword_filter, render_sidebar_admin, to_en
from app.backup import backup_db
from app.crud import save_df

# ── edit form helpers ─────────────────────────────────────────────────────────
def _sf(v, d=0.0):
    try:
        f = float(v); return f if math.isfinite(f) else d
    except Exception: return d

def _ss(v):
    if v is None: return ""
    if isinstance(v, float) and not math.isfinite(v): return ""
    return str(v)

def _sb(v):
    try: return bool(float(v))
    except Exception: return bool(v) if v else False

@st.dialog("✍️ 編輯商品", width="large")
def _edit_dialog():
    pid  = st.session_state.get("edit_item_pid",  "")
    name = st.session_state.get("edit_item_name", "")
    df_all = load_menu_df_cn()
    import pandas as pd
    match = df_all[df_all["產品編號"].astype(str).str.strip() == pid] if pid else pd.DataFrame()
    if match.empty and name:
        match = df_all[df_all["產品名稱"].astype(str).str.strip() == name]
    if match.empty:
        st.error(f"找不到商品（編號:{pid} / 名稱:{name}）")
        return
    row = match.iloc[0]; idx = match.index[0]
    with st.form("dlg_edit_form"):
        st.markdown("**基本資訊**")
        c1, c2 = st.columns(2)
        with c1:
            product_name = st.text_input("產品名稱", value=_ss(row.get("產品名稱")))
            category     = st.text_input("分類",     value=_ss(row.get("分類")))
            vendor       = st.text_input("廠商",     value=_ss(row.get("廠商")))
        with c2:
            product_id   = st.text_input("產品編號", value=_ss(row.get("產品編號")))
            unit         = st.text_input("單位數量", value=_ss(row.get("單位")))
            price_note   = st.text_input("售價備註", value=_ss(row.get("售價備註")))
            shelf_life   = st.text_input("保存期限", value=_ss(row.get("保存期限")))
        st.markdown("**價格 / 成本**")
        c1, c2 = st.columns(2)
        with c1: sale_price = st.number_input("產品售價", value=_sf(row.get("產品售價")), min_value=0.0, step=1.0)
        with c2: pkg_price  = st.number_input("單包進貨價", value=_sf(row.get("單包進貨價")), min_value=0.0, step=0.1)
        st.markdown("**重量**")
        c1, c2 = st.columns(2)
        with c1: unit_grams = st.number_input("商品單位克數 (g)", value=_sf(row.get("商品單位克數")), min_value=0.0, step=1.0)
        with c2: pkg_weight = st.number_input("單包重量 (g)", value=_sf(row.get("單包重量")), min_value=0.0, step=1.0)
        if pkg_weight > 0 and unit_grams > 0 and pkg_price > 0:
            calc_cost = round(pkg_price * (unit_grams / pkg_weight), 2)
            st.info(f"📊 單位成本 = {pkg_price} × ({unit_grams}g / {pkg_weight}g) = **{calc_cost} 元**")
        else:
            calc_cost = _sf(row.get("單位成本"))
            st.info(f"📊 單位成本（現有）：{calc_cost} 元（請填入重量以自動計算）")
        st.markdown("**狀態**")
        c1, c2, c3 = st.columns(3)
        with c1: is_available = st.checkbox("是否上架",     value=_sb(row.get("是否上架")))
        with c2: is_menu_item = st.checkbox("是否菜單品項", value=_sb(row.get("是否菜單品項")))
        with c3: is_prepared  = st.checkbox("是否現場準備", value=_sb(row.get("是否現場準備")))
        note = st.text_area("備註", value=_ss(row.get("備註")), height=80)
        submitted = st.form_submit_button("💾 儲存", use_container_width=True, type="primary")
    if submitted:
        backup_db("before_single_save")
        df_new = load_menu_df_cn()
        df_new.at[idx, "產品編號"]     = product_id
        df_new.at[idx, "產品名稱"]     = product_name
        df_new.at[idx, "分類"]         = category
        df_new.at[idx, "廠商"]         = vendor
        unit_cost = round(pkg_price * (unit_grams / pkg_weight), 2) if pkg_weight > 0 and unit_grams > 0 and pkg_price > 0 else _sf(row.get("單位成本"))
        df_new.at[idx, "產品售價"]     = sale_price
        df_new.at[idx, "單位成本"]     = unit_cost
        df_new.at[idx, "單包進貨價"]   = pkg_price
        df_new.at[idx, "商品單位克數"] = unit_grams
        df_new.at[idx, "單包重量"]     = pkg_weight
        df_new.at[idx, "單位"]         = unit
        df_new.at[idx, "售價備註"]     = price_note
        df_new.at[idx, "是否上架"]     = 1.0 if is_available else 0.0
        df_new.at[idx, "是否菜單品項"] = "1" if is_menu_item else "0"
        df_new.at[idx, "是否現場準備"] = "1" if is_prepared  else "0"
        df_new.at[idx, "備註"]         = note
        df_new.at[idx, "保存期限"]     = shelf_life
        save_df(to_en(df_new))
        st.session_state.pop("edit_item_pid",  None)
        st.session_state.pop("edit_item_name", None)
        st.session_state["open_edit_dialog"] = False
        st.success("已儲存！")
        st.rerun()

def _read_version():
    try:
        v = Path(__file__).resolve().parents[2] / "VERSION.txt"
        if v.exists():
            return v.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "—"

APP_VERSION = _read_version()

st.set_page_config(page_title="產品總覽｜菜單儀表板", layout="wide")
user = require_page("顯示")
log_access(user, "顯示")
apply_base_css()
render_sidebar_admin()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #f0f2f5 !important; }
.block-container { padding-top: 4rem !important; max-width: 900px !important; }
.page-title    { font-size: 1.85rem; font-weight: 800; color: #1a1a1a; line-height: 1.2; margin: 0; }
.page-subtitle { font-size: 0.88rem; color: #9e9e9e; margin-top: 3px; }

/* Search & multiselect */
.stTextInput > div > div > input {
    border-radius: 12px !important; background: white !important;
    border-color: #e8e8e8 !important; font-size: 0.9rem !important; padding: 10px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3dba6e !important; box-shadow: 0 0 0 2px rgba(61,186,110,0.15) !important;
}
.stMultiSelect > div { border-radius: 12px !important; background: white !important; border-color: #e8e8e8 !important; }
.stMultiSelect [data-baseweb="tag"] { background-color: #e0e7ff !important; border-radius: 99px !important; }
.stMultiSelect [data-baseweb="tag"] span { color: #3730a3 !important; font-weight: 600 !important; }

/* Category tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px !important; border-bottom: 2px solid #e8e8e8 !important; background: transparent !important; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; padding: 7px 16px !important; font-size: 0.82rem !important; font-weight: 500 !important; color: #9e9e9e !important; background: transparent !important; border: none !important; }
.stTabs [aria-selected="true"] { color: #2ea85a !important; background: white !important; border-bottom: 2px solid #3dba6e !important; font-weight: 700 !important; }
.stTabs [data-testid="stTabsContent"] { padding-top: 14px !important; border: none !important; background: transparent !important; }

/* === Expander as product card (same style as todo) === */
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
    padding: 4px 20px 18px 20px !important;
}

/* Product meta tags */
.prod-tag {
    display: inline-block; border-radius: 99px;
    padding: 2px 10px; font-size: 0.73rem; font-weight: 600; margin-right: 4px;
}
.prod-tag-cat    { background: #f0f0f0; color: #555; }
.prod-tag-vendor { background: #e0e7ff; color: #3730a3; }
.prod-tag-status { background: #e8f5ee; color: #2ea85a; }
.prod-tag-off    { background: #fef2f2; color: #ef4444; }

.prod-meta { color: #9e9e9e; font-size: 0.80rem; margin-bottom: 10px; line-height: 1.8; }
.prod-detail-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5; font-size: 0.85rem; }
.prod-detail-row:last-child { border-bottom: none; }
.prod-detail-key { color: #9e9e9e; font-weight: 600; }
.prod-detail-val { color: #1a1a1a; font-weight: 700; text-align: right; }

/* Action button inside card */
[data-testid="stExpander"] .stButton > button[kind="secondary"] {
    border-radius: 8px !important; font-size: 0.80rem !important;
    border-color: #e8e8e8 !important; color: #555 !important; padding: 4px 12px !important;
}
button[kind="primary"] { background-color: #3dba6e !important; border-color: #3dba6e !important; border-radius: 99px !important; font-weight: 600 !important; }

/* Empty state */
.empty-todo { text-align: center; padding: 48px 20px; color: #bbb; }
.empty-todo-icon { font-size: 2.5rem; }
.empty-todo-text { font-size: 0.9rem; margin-top: 8px; }
hr { border-color: #f0f0f0 !important; margin: 10px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

def _num(v):
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except Exception:
        return None

def _fmt_money(v):
    v = _num(v)
    if v is None: return ""
    return f"{int(v):,}" if abs(v - int(v)) < 1e-9 else f"{v:,.1f}"

def _col(*names):
    return next((c for c in names if c in df.columns), None)

# ── data loading ──────────────────────────────────────────────────────────────

df = load_menu_df_cn()
if df.empty:
    st.warning("目前沒有資料。請到 Admin 頁面匯入 CSV。")
    st.stop()

df = add_margin_cols(df)

name_col   = _col("產品名稱", "品名", "name")
price_col  = _col("產品售價", "單位價格", "售價", "price")
cat_col    = _col("分類", "類別", "category")
vendor_col = _col("廠商", "供應商", "vendor")
pid_col    = "產品編號" if "產品編號" in df.columns else None

# ── edit dialog trigger ───────────────────────────────────────────────────────
if st.session_state.get("open_edit_dialog"):
    _edit_dialog()

# ── page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="page-title">產品總覽</div>'
    f'<div class="page-subtitle">菜單儀表板 · v{APP_VERSION}</div>',
    unsafe_allow_html=True,
)

# ── filter bar ────────────────────────────────────────────────────────────────
f1, f2 = st.columns([3, 2])
with f1:
    keyword = st.text_input("搜尋", placeholder="🔍 搜尋商品、廠商、分類…", label_visibility="collapsed")

all_vendors = []
if vendor_col:
    all_vendors = sorted([v for v in df[vendor_col].dropna().astype(str).unique() if v.strip() and v.lower() != "none"])

with f2:
    selected_vendors = st.multiselect(
        "廠商篩選", options=all_vendors,
        placeholder="🏭 篩選廠商…",
        label_visibility="collapsed",
    ) if all_vendors else []

# ── base filter ───────────────────────────────────────────────────────────────
df_base = keyword_filter(df, keyword.strip()) if keyword.strip() else df.copy()
if selected_vendors and vendor_col:
    df_base = df_base[df_base[vendor_col].astype(str).isin(selected_vendors)]

# ── product card renderer ─────────────────────────────────────────────────────
# detail fields to show inside card (skip name/cat/vendor shown in header/tags)
SKIP_IN_CARD = {"產品名稱", "品名", "name", "分類", "類別", "category", "廠商", "供應商", "vendor"}

def _render_cards(data, tab_key: str):
    if data.empty:
        st.markdown(
            '<div class="empty-todo">'
            '<div class="empty-todo-icon">🔍</div>'
            '<div class="empty-todo-text">沒有符合的商品</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    for i, (_, r) in enumerate(data.iterrows()):
        nm  = str(r.get(name_col, "")) if name_col else f"商品 {i+1}"
        pr  = _fmt_money(r.get(price_col)) if price_col else ""
        pid = str(r.get(pid_col, "")) if pid_col else f"idx_{int(r.name)}"

        # Expander label: name + price
        price_suffix = f"  ·  {pr} 元" if pr else ""
        exp_label = f"🛒 {nm}{price_suffix}"

        with st.expander(exp_label, expanded=False):
            # ── meta tags (vendor + category + status) ──
            tags_html = ""
            if vendor_col:
                v = str(r.get(vendor_col, "") or "")
                if v and v.lower() not in ("", "none", "nan"):
                    tags_html += f'<span class="prod-tag prod-tag-vendor">🏭 {v}</span>'
            if cat_col:
                c = str(r.get(cat_col, "") or "")
                if c and c.lower() not in ("", "none", "nan"):
                    tags_html += f'<span class="prod-tag prod-tag-cat">📂 {c}</span>'
            # availability badge
            avail_val = str(r.get("是否上架", "") or "")
            if avail_val in ("1", "1.0", "True", "true", "是"):
                tags_html += '<span class="prod-tag prod-tag-status">✅ 上架</span>'
            elif avail_val:
                tags_html += '<span class="prod-tag prod-tag-off">❌ 下架</span>'

            if tags_html:
                st.markdown(f'<div class="prod-meta">{tags_html}</div>', unsafe_allow_html=True)

            # ── key-value detail rows ──
            detail_rows = []
            show_cols = [
                ("產品售價", "售價"),
                ("單位成本", "成本"),
                ("單位",     "單位數量"),
                ("商品單位克數", "單位克數"),
                ("單包重量", "單包重量"),
                ("保存期限", "保存期限"),
                ("售價備註", "備註"),
                ("是否菜單品項", "菜單品項"),
                ("是否現場準備", "現場準備"),
                ("備註",         "備註（其他）"),
            ]
            WEIGHT_COLS = {"商品單位克數", "單包重量"}
            for col_key, label in show_cols:
                if col_key not in df.columns:
                    continue
                val = r.get(col_key)
                if val is None or (isinstance(val, float) and not math.isfinite(val)):
                    val_s = "—" if col_key in WEIGHT_COLS else None
                    if val_s is None:
                        continue
                else:
                    val_s = str(val).strip()
                    if not val_s or val_s.lower() in ("nan", "none", ""):
                        val_s = "—" if col_key in WEIGHT_COLS else None
                        if val_s is None:
                            continue
                    elif val_s in ("0", "0.0") and col_key not in WEIGHT_COLS:
                        continue
                    elif val_s in ("0", "0.0") and col_key in WEIGHT_COLS:
                        val_s = "—"
                if col_key.startswith("是否"):
                    val_s = "是" if val_s in ("1", "1.0", "True", "true", "是") else "否"
                    if val_s == "否":
                        continue
                detail_rows.append((label, val_s))

            if detail_rows:
                rows_html = "".join(
                    f'<div class="prod-detail-row">'
                    f'<span class="prod-detail-key">{lbl}</span>'
                    f'<span class="prod-detail-val">{val}</span>'
                    f'</div>'
                    for lbl, val in detail_rows
                )
                st.markdown(rows_html, unsafe_allow_html=True)
                st.divider()

            # ── edit button ──
            if st.button("✏️ 編輯", key=f"{tab_key}_edit_{pid}_{i}", type="primary"):
                st.session_state["edit_item_pid"]    = pid if pid_col else ""
                st.session_state["edit_item_name"]   = nm
                st.session_state["open_edit_dialog"] = True
                st.rerun()

# ── category tabs ─────────────────────────────────────────────────────────────
if cat_col and cat_col in df_base.columns:
    cats = sorted([c for c in df_base[cat_col].dropna().astype(str).unique() if c.strip()])
else:
    cats = []

tab_labels = [f"全部  {len(df_base)}"] + [
    f"{c}  {int((df_base[cat_col].astype(str) == c).sum())}" for c in cats
]
tabs = st.tabs(tab_labels)

with tabs[0]:
    _render_cards(df_base, "t0")

for i, cat in enumerate(cats):
    with tabs[i + 1]:
        df_cat = df_base[df_base[cat_col].astype(str) == cat]
        _render_cards(df_cat, f"t{i+1}")
