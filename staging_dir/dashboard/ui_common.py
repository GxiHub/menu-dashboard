import os
import streamlit as st
import pandas as pd

from app.crud import get_all
from app.schema import EN_TO_CN, CN_TO_EN


def apply_base_css() -> None:
    """Unified design-system CSS with custom properties + mobile (RWD) tweaks."""
    st.markdown(
        """
<style>
/* ══════════════ Design Tokens (CSS Custom Properties) ══════════════ */
:root {
  --color-primary: #3dba6e;
  --color-primary-hover: #34a660;
  --color-bg: #f0f2f5;
  --color-card: white;
  --color-border: #e8e8e8;
  --color-text: #1a1a1a;
  --color-text-muted: #9e9e9e;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 99px;
}

/* ══════════════ Global ══════════════ */
.stApp { background: var(--color-bg); }
.block-container { padding-top: 1.0rem; padding-bottom: 1.6rem; max-width: 1200px; }
h1, h2, h3 { letter-spacing: -0.2px; color: var(--color-text); }
hr { border-color: var(--color-border); }

/* ══════════════ Page Title / Subtitle ══════════════ */
.page-title {
  font-size: 1.6rem; font-weight: 700; color: var(--color-text);
  margin-bottom: 0.2rem; letter-spacing: -0.3px;
}
.page-subtitle {
  font-size: 0.95rem; color: var(--color-text-muted);
  margin-bottom: 1.2rem;
}

/* ══════════════ Card-like Metrics ══════════════ */
[data-testid="stMetric"] {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 12px 14px;
}

/* ══════════════ Buttons ══════════════ */
div.stButton > button {
  border-radius: var(--radius-pill);
  min-height: 44px;
  font-weight: 600;
  transition: all 0.15s ease;
}
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--color-primary);
  border: none;
  color: white;
  box-shadow: 0 2px 6px rgba(61,186,110,0.25);
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="stBaseButton-primary"]:hover {
  background: var(--color-primary-hover);
  box-shadow: 0 4px 12px rgba(61,186,110,0.35);
}

/* ══════════════ Tabs ══════════════ */
div[data-testid="stTabs"] > div[role="tablist"] {
  flex-wrap: nowrap !important;
  overflow-x: auto !important;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
  gap: 4px;
}
div[data-testid="stTabs"] > div[role="tablist"]::-webkit-scrollbar { display: none; }
div[data-testid="stTabs"] button[role="tab"] {
  flex-shrink: 0;
  white-space: nowrap;
  border-radius: var(--radius-pill);
  padding: 6px 18px;
  font-weight: 500;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  background: var(--color-primary);
  color: white;
}

/* ══════════════ Expander Cards ══════════════ */
div[data-testid="stExpander"] {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s ease;
  overflow: hidden;
}
div[data-testid="stExpander"]:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* ══════════════ Inputs ══════════════ */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--color-border);
  transition: border-color 0.15s ease;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 2px rgba(61,186,110,0.15);
}

/* ══════════════ Multiselect ══════════════ */
div[data-testid="stMultiSelect"] > div {
  border-radius: var(--radius-md) !important;
}
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
  background: var(--color-primary);
  border-radius: var(--radius-sm);
}

/* ══════════════ Data Tables: mobile scroll ══════════════ */
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
  overflow-x: auto;
}

/* ══════════════ Dialog: mobile fix ══════════════ */
@media (max-width: 640px) {
  div[data-testid="stDialog"] > div {
    width: 95vw !important;
    max-width: 95vw !important;
  }
}

/* ══════════════ Top Navigation: horizontally scrollable on mobile ══════════════ */
[data-testid=stNavigation] {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}
[data-testid=stNavigation]::-webkit-scrollbar { display: none !important; }
[data-testid=stNavigation] ul {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
}
[data-testid=stNavigation] li {
    flex-shrink: 0 !important;
    white-space: nowrap !important;
}

/* ══════════════ RWD for phones ══════════════ */
@media (max-width: 768px) {
  .block-container { padding-left: 0.7rem; padding-right: 0.7rem; }
  h1 { font-size: 1.35rem; }
  h2 { font-size: 1.1rem; }
  h3 { font-size: 1.0rem; }
  [data-testid="stMetricValue"] { font-size: 1.6rem; }
  [data-testid="stMetricLabel"] { font-size: 0.95rem; }
  div.stButton > button { min-height: 48px; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def to_cn(df_en: pd.DataFrame) -> pd.DataFrame:
    return df_en.rename(columns={c: EN_TO_CN.get(c, c) for c in df_en.columns})


def to_en(df_cn: pd.DataFrame) -> pd.DataFrame:
    return df_cn.rename(columns={c: CN_TO_EN.get(c, c) for c in df_cn.columns})


def safe_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0)


@st.cache_data(ttl=60)
def load_menu_df_cn() -> pd.DataFrame:
    df_en = get_all()
    if df_en is None or df_en.empty:
        return pd.DataFrame()
    return to_cn(df_en)


def invalidate_menu_cache() -> None:
    """Clear the cached menu DataFrame so next call re-reads DB."""
    load_menu_df_cn.clear()


def add_margin_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Add 毛利 / 毛利率 columns if cost & price exist."""
    df = df.copy()
    cost_col = "單位價格" if "單位價格" in df.columns else None
    price_col = "產品售價" if "產品售價" in df.columns else None
    if cost_col and price_col:
        df["_成本"] = safe_num(df[cost_col])
        df["_售價"] = safe_num(df[price_col])
        df["毛利"] = df["_售價"] - df["_成本"]
        df["毛利率"] = (df["毛利"] / df["_售價"].replace({0: None})).fillna(0)
    else:
        df["毛利"] = 0
        df["毛利率"] = 0
    return df


def keyword_filter(df: pd.DataFrame, kw: str) -> pd.DataFrame:
    kw = (kw or "").strip()
    if not kw:
        return df
    mask = df.astype(str).apply(lambda s: s.str.contains(kw, case=False, na=False))
    return df[mask.any(axis=1)]


def render_sidebar_admin() -> None:
    pass
