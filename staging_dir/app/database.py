
import os
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "menu.db")

_engine = None

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    eng = get_engine()
    with eng.connect():
        pass

def get_engine():
    global _engine
    if _engine is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    return _engine
