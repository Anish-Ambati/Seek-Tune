# utils/__init__.py

import logging
from pathlib import Path

# -----------------------------
# LOGGER (GLOBAL)
# -----------------------------

def get_logger(name: str = "seek_tune_py"):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# -----------------------------
# DIRECTORY UTILITIES
# -----------------------------

def create_folder(path: Path):
    """
    Safely create a directory if it doesn't exist.
    Mirrors Go's utils.CreateFolder.
    """
    path.mkdir(parents=True, exist_ok=True)
