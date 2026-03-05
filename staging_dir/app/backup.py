
import os
import shutil
from datetime import datetime
from app.database import DB_PATH

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, "data", "backup")
PREV_PATH = os.path.join(BACKUP_DIR, "menu_prev.db")

def backup_db(reason="manual"):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        return False

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stamped = os.path.join(BACKUP_DIR, f"menu_{ts}_{reason}.db")

    shutil.copy2(DB_PATH, PREV_PATH)
    shutil.copy2(DB_PATH, stamped)
    return True

def restore_prev():
    if not os.path.exists(PREV_PATH):
        return False
    shutil.copy2(PREV_PATH, DB_PATH)
    return True
