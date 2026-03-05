
import pandas as pd
from sqlalchemy import text
from app.database import get_engine, init_db

def get_all():
    init_db()
    try:
        return pd.read_sql(text("select * from menu_items"), get_engine())
    except:
        return pd.DataFrame()

def save_df(df):
    init_db()
    df.to_sql("menu_items", get_engine(), if_exists="replace", index=False)
