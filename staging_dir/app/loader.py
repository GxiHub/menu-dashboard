import os
import pandas as pd
from typing import Optional

from app.database import init_db, get_engine
from app.schema import CN_TO_EN

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_CSV = os.path.join(DATA_DIR, "menu_items.csv")

# DB 需要的核心欄位（英文）
CORE_COLS = [
    "product_id","product_name","category","unit_qty","unit",
    "purchase_weight","unit_weight","unit_weight_unit",
    "sale_price","price_note","vendor","unit_cost",
    "is_prepared_on_site","is_menu_item","is_available","note"
]

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # 1) 如果是中文欄位，轉成英文
    renamed = {}
    for c in df.columns:
        if c in CN_TO_EN:
            renamed[c] = CN_TO_EN[c]
    if renamed:
        df = df.rename(columns=renamed)

    # 2) 補齊缺欄
    for c in CORE_COLS:
        if c not in df.columns:
            df[c] = pd.NA

    # 3) 只保留核心欄位（避免 csv 多出奇怪欄位干擾）
    df = df[CORE_COLS]
    return df

def load_to_db(csv_path: Optional[str] = None):
    path = csv_path or DEFAULT_CSV
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到 CSV：{path}")

    init_db()
    df = pd.read_csv(path)

    df = _normalize_columns(df)

    df.to_sql("menu_items", get_engine(), if_exists="replace", index=False)
    return df
