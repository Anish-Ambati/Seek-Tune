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


def _youtube_download_by_search(query: str, tmp_audio_base: Path) -> tuple[Path, dict]:
    """
    Use yt-dlp with 'ytsearch1:' to download the best audio for a search query.
    Saves to tmp_audio_base.<ext> and returns (downloaded_file_path, info_dict).
    """
    create_folder(tmp_audio_base.parent)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(tmp_audio_base.with_suffix(".%(ext)s")),
        "quiet": True,
        "noprogress": True,
        "overwrites": True,
        "cachedir": False,
    }

    logger.info(f"[dl] Searching YouTube for: {query}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)

    # When using ytsearch1, info["entries"][0] contains the actual video
    if "entries" in info and info["entries"]:
        info_video = info["entries"][0]
    else:
        info_video = info

    ext = info_video.get("ext", "webm")
    vid_id = info_video.get("id")

    candidate1 = tmp_audio_base.with_suffix(f".{ext}")
    candidate2 = tmp_audio_base.parent / f"{vid_id}.{ext}"

    if candidate1.exists():
        downloaded_path = candidate1
    elif candidate2.exists():
        downloaded_path = candidate2
    else:
        # As a last resort, try to derive filename from info (some yt-dlp configs)
        # but raise if not found
        raise FileNotFoundError(
            f"[dl] Could not find downloaded file at {candidate1} or {candidate2}"
        )

    logger.info(f"[dl] YouTube audio downloaded: {downloaded_path}")
    return downloaded_path, info_video


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
          "spotify_url": str,
          "youtube_url": str
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
    downloaded_path, info_video = _youtube_download_by_search(search_query, tmp_audio_base)

    # Try to find a canonical YouTube URL
    yt_url = info_video.get("webpage_url")
    if not yt_url:
        vid_id = info_video.get("id")
        if vid_id:
            yt_url = f"https://www.youtube.com/watch?v={vid_id}"
        else:
            yt_url = None

    logger.info(f"[dl] Selected YouTube URL: {yt_url}")

    # 4) Convert to WAV in SONGS_DIR
    create_folder(SONGS_DIR)
    wav_target = SONGS_DIR / f"{safe_title} - {safe_artist}.wav"

    wav_path = convert_to_wav(str(downloaded_path), str(wav_target))

    # 5) Fingerprint and insert into DB
    # NOTE: generate_fingerprint should accept spotify_url and youtube_url (see fingerprint changes)
    song_id, num_hashes = generate_fingerprint(
        wav_path,
        title=title,
        artist=artist,
        spotify_url=spotify_url,
        youtube_url=yt_url,
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
        "spotify_url": spotify_url,
        "youtube_url": yt_url,
    }
