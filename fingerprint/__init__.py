# fingerprint/__init__.py

from pathlib import Path

from fingerprint.spectrogram import generate_spectrogram
from fingerprint.peak_picker import find_peaks
from fingerprint.hasher import generate_hashes
from db import init_db, insert_song, insert_fingerprints
from utils import get_logger

logger = get_logger("fingerprint")


def generate_fingerprint(file_path: str, title: str | None = None, artist: str | None = None, spotify_url: str = None, youtube_url: str = None):
    """
    Full pipeline:
        audio file -> spectrogram -> peaks -> hashes -> DB

    Returns:
        (song_id, num_hashes)
    """

    file_path = str(file_path)
    p = Path(file_path)

    if not p.exists():
        raise FileNotFoundError(f"Audio file does not exist: {file_path}")

    # Initialize DB (create tables if needed)
    init_db()

    # 1) Spectrogram
    spec = generate_spectrogram(file_path)

    # 2) Peaks
    peaks = find_peaks(spec)

    # 3) Hashes
    hashes = generate_hashes(peaks)

    if not hashes:
        logger.warning(f"No hashes generated for file: {file_path}")

    # 4) Insert song into DB
    inferred_title = title if title is not None else p.stem
    inferred_artist = artist if artist is not None else "Unknown Artist"

    song_id = insert_song(
        title=inferred_title,
        artist=inferred_artist,
        path=file_path,
        spotify_url=spotify_url,
        youtube_url=youtube_url
    )

    # 5) Insert fingerprints
    insert_fingerprints(song_id, hashes)

    logger.info(
        f"Fingerprint for '{inferred_title}' by '{inferred_artist}' saved in DB successfully "
        f"({len(hashes)} hashes)."
    )

    return song_id, len(hashes)
