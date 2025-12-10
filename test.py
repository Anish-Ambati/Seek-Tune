# test_imports.py
from config import SONGS_DIR, DB_TYPE
from utils import get_logger

print("SONGS_DIR:", SONGS_DIR)
print("DB_TYPE:", DB_TYPE)

logger = get_logger()
logger.info("Logger working ✅")
