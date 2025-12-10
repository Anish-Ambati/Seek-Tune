# downloader/service.py

from pathlib import Path
import yt_dlp

from utils import get_logger
from config import SONGS_DIR, TMP_DIR
from utils import create_folder
from spotify.client import SpotifyClient
from downloader.ffmpeg import convert_to_wav
from fingerprint import generate_fingerprint

logger = get_logger("download_service")


def _youtube_download_by_search(query: str, tmp_audio_base: Path) -> Path:
    """
    Use yt-dlp with 'ytsearch1:' to download the best audio for a search query.
    Saves to tmp_audio_base.<ext> and returns the actual downloaded file path.
    """
    create_folder(tmp_audio_base.parent)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(tmp_audio_base.with_suffix(".%(ext)s")),
        "quiet": True,
        "noprogress": True,
        "overwrites": True,       # <--- ensure it overwrites
        "cachedir": False,        # <--- avoid reusing cache
    }

    logger.info(f"[dl] Searching YouTube for: {query}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)

    # When using ytsearch1, info["entries"][0] contains the actual video
    if "entries" in info:
        info = info["entries"][0]

    ext = info.get("ext", "webm")
    vid_id = info.get("id")

    # Unique temp candidate based on our template
    candidate1 = tmp_audio_base.with_suffix(f".{ext}")
    candidate2 = tmp_audio_base.parent / f"{vid_id}.{ext}"

    if candidate1.exists():
        downloaded_path = candidate1
    elif candidate2.exists():
        downloaded_path = candidate2
    else:
        raise FileNotFoundError(
            f"[dl] Could not find downloaded file at {candidate1} or {candidate2}"
        )

    logger.info(f"[dl] YouTube audio downloaded: {downloaded_path}")
    return downloaded_path


def download_and_fingerprint_from_spotify(spotify_url: str) -> dict:
    """
    Full pipeline for the 'download' command:

        Spotify URL -> track info (title, artist)
                     -> YouTube search
                     -> audio download
                     -> WAV conversion
                     -> fingerprint + DB insert

    Returns:
        {
          "song_id": int,
          "title": str,
          "artist": str,
          "hashes": int,
          "wav_path": str,
        }
    """
    client = SpotifyClient()

    # 1) Get track metadata from Spotify
    track_info = client.get_track_info(spotify_url)
    title = track_info["title"]
    artist = track_info["artist"]

    logger.info(f"[dl] Download pipeline for: '{title}' by '{artist}'")

    # 2) Build YouTube search query
    search_query = f"{title} {artist} audio"

    # Make a SAFE filename base for temp download (unique per track)
    safe_title = "".join(c for c in title if c not in r'\/:*?"<>|')
    safe_artist = "".join(c for c in artist if c not in r'\/:*?"<>|')
    tmp_audio_base = TMP_DIR / f"spotify_dl_{safe_title}_{safe_artist}"

    # 3) Download best audio using yt-dlp search
    downloaded_path = _youtube_download_by_search(search_query, tmp_audio_base)

    # 4) Convert to WAV in SONGS_DIR
    create_folder(SONGS_DIR)
    wav_target = SONGS_DIR / f"{safe_title} - {safe_artist}.wav"

    wav_path = convert_to_wav(str(downloaded_path), str(wav_target))

    # 5) Fingerprint and insert into DB
    song_id, num_hashes = generate_fingerprint(
        wav_path,
        title=title,
        artist=artist,
    )

    logger.info(
        f"[dl] Pipeline complete: song_id={song_id}, hashes={num_hashes}, wav='{wav_path}'"
    )

    return {
        "song_id": song_id,
        "title": title,
        "artist": artist,
        "hashes": num_hashes,
        "wav_path": str(wav_path),
    }
