# config.py
from pathlib import Path
import os

# -----------------------------
# BASE DIRECTORIES
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent

SONGS_DIR = BASE_DIR / "songs"
RECORDINGS_DIR = BASE_DIR / "recordings"
TMP_DIR = BASE_DIR / "tmp"
DB_DIR = BASE_DIR / "db"

# -----------------------------
# DATABASE CONFIG
# -----------------------------
# Matches Go repo behavior:
# DB_TYPE can be: sqlite | mongo (default: sqlite)

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

SQLITE_DB_PATH = DB_DIR / "seek_tune.db"

MONGO_USER = os.getenv("DB_USER", "root")
MONGO_PASSWORD = os.getenv("DB_PASSWORD", "password")
MONGO_NAME = os.getenv("DB_NAME", "seek_tune_db")
MONGO_HOST = os.getenv("DB_HOST", "localhost")
MONGO_PORT = os.getenv("DB_PORT", "27017")

# -----------------------------
# SPOTIFY CONFIG
# -----------------------------

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# -----------------------------
# SERVER CONFIG
# -----------------------------

DEFAULT_PROTO = "http"
DEFAULT_PORT = 5000
