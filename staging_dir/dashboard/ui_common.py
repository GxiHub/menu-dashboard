import streamlit as st
import pandas as pd

from app.crud import get_all
from app.schema import EN_TO_CN, CN_TO_EN


def apply_base_css() -> None:
    """Base UI styles + mobile (RWD) tweaks."""
    st.markdown(
        """
<style>
/* Global spacing */
.block-container { padding-top: 1.0rem; padding-bottom: 1.6rem; max-width: 1200px; }

/* Card-like metrics */
[data-testid="stMetric"] {
  background: rgba(246,247,251,1);
  border: 1px solid rgba(17,24,39,0.08);
  border-radius: 16px;
  padding: 12px 14px;
}

/* Make data tables easier to scroll on mobile */
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
  overflow-x: auto;
}

/* --- RWD for phones --- */
@media (max-width: 768px) {
  .block-container { padding-left: 0.7rem; padding-right: 0.7rem; }
  h1 { font-size: 1.35rem; }
  h2 { font-size: 1.1rem; }
  h3 { font-size: 1.0rem; }
  [data-testid="stMetricValue"] { font-size: 1.6rem; }
  [data-testid="stMetricLabel"] { font-size: 0.95rem; }
}

/* ── Top navigation: horizontally scrollable on mobile ── */
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


/* Reduce top/bottom whitespace of widgets */
div.stButton > button { border-radius: 12px; }
h1, h2, h3 { letter-spacing: -0.2px; }
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


def load_menu_df_cn() -> pd.DataFrame:
    df_en = get_all()
    if df_en is None or df_en.empty:
        return pd.DataFrame()
    return to_cn(df_en)


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
