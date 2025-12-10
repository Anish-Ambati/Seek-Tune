# db/sqlite.py

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

from config import SQLITE_DB_PATH, DB_DIR
from utils import create_folder, get_logger

logger = get_logger("sqlite_db")

# -----------------------------
# SETUP
# -----------------------------

create_folder(DB_DIR)

engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------------
# TABLES
# -----------------------------

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    path = Column(String, unique=True, index=True)


class Fingerprint(Base):
    __tablename__ = "fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"))
    hash_value = Column(String, index=True)
    offset = Column(Float)

# Index for fast lookup by hash
Index("idx_hash_lookup", Fingerprint.hash_value)

# -----------------------------
# DB INIT
# -----------------------------

def init_db():
    """Create tables if they do not exist."""
    logger.info("Initializing SQLite database...")
    Base.metadata.create_all(bind=engine)
    logger.info("SQLite DB ready.")

# -----------------------------
# INSERT OPERATIONS
# -----------------------------

def insert_song(title: str, artist: str, path: str) -> int:
    session = SessionLocal()

    song = Song(
        title=title,
        artist=artist,
        path=path,
    )

    session.add(song)
    session.commit()
    session.refresh(song)
    session.close()

    logger.info(f"Inserted song: {title} by {artist}")
    return song.id


def insert_fingerprints(song_id: int, hashes: list):
    """
    hashes = list of (hash_value, offset)
    """
    session = SessionLocal()

    for hash_value, offset in hashes:
        fp = Fingerprint(
            song_id=song_id,
            hash_value=hash_value,
            offset=float(offset),
        )
        session.add(fp)

    session.commit()
    session.close()

    logger.info(f"Inserted {len(hashes)} fingerprints for song_id={song_id}")

# -----------------------------
# QUERY OPERATIONS
# -----------------------------

def get_fingerprints_by_hash(hash_value: str):
    session = SessionLocal()

    results = (
        session.query(Fingerprint)
        .filter(Fingerprint.hash_value == hash_value)
        .all()
    )

    session.close()
    return results

# -----------------------------
# ERASE OPERATIONS
# -----------------------------

def delete_db():
    """
    Delete the entire SQLite database file.
    Mirrors Go's `erase db` behavior.
    """
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()
        logger.info("SQLite database deleted.")
    else:
        logger.warning("SQLite database does not exist.")

       
def get_song_by_id(song_id: int):
    """Fetch a Song row by its ID."""
    session = SessionLocal()
    song = (
        session.query(Song)
        .filter(Song.id == song_id)
        .first()
    )
    session.close()
    return song
