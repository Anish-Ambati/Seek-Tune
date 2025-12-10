# db/__init__.py

from config import DB_TYPE
from utils import get_logger

logger = get_logger("db")

# Import the correct DB backend based on config
if DB_TYPE == "mongo":
    from db.mongo import (
        init_db,
        insert_song,
        insert_fingerprints,
        get_fingerprints_by_hash,
        delete_db,
    )
    logger.info("Using MongoDB backend")
else:
    # Default = SQLite
    from db.sqlite import (
    init_db,
    insert_song,
    insert_fingerprints,
    get_fingerprints_by_hash,
    get_song_by_id,
    delete_db,
    )

    logger.info("Using SQLite backend")
