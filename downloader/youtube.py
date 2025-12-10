# downloader/youtube.py

from pathlib import Path
import yt_dlp

from config import SONGS_DIR, TMP_DIR
from utils import create_folder, get_logger
from downloader.ffmpeg import convert_to_wav

logger = get_logger("youtube_downloader")


def download_youtube_audio(youtube_url: str, title_hint: str | None = None):
    """
    Download audio from a YouTube URL using yt-dlp,
    convert it to normalized WAV, save into SONGS_DIR.

    Returns:
        path_to_wav (str)
    """

    create_folder(SONGS_DIR)
    create_folder(TMP_DIR)

    logger.info(f"[yt] Downloading from YouTube: {youtube_url}")

    # Temporary output (any audio format)
    tmp_audio = TMP_DIR / "yt_audio.%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(tmp_audio),
        "quiet": True,
        "noprogress": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)

    # Determine actual downloaded file path
    # yt-dlp returns a dict with 'ext' and 'id'
    ext = info.get("ext", "webm")
    downloaded_path = TMP_DIR / f"yt_audio.{ext}"

    if not downloaded_path.exists():
        # fallback: sometimes outtmpl uses video id
        vid_id = info.get("id")
        alt_path = TMP_DIR / f"{vid_id}.{ext}"
        if alt_path.exists():
            downloaded_path = alt_path
        else:
            raise FileNotFoundError(
                f"[yt] Could not locate downloaded file at {downloaded_path} or {alt_path}"
            )

    logger.info(f"[yt] Downloaded file: {downloaded_path}")

    # Decide final WAV filename
    if title_hint:
        safe_name = "".join(c for c in title_hint if c not in r'\/:*?"<>|')
        output_wav = SONGS_DIR / f"{safe_name}.wav"
    else:
        output_wav = SONGS_DIR / "downloaded_track.wav"

    # Convert to WAV
    wav_path = convert_to_wav(str(downloaded_path), str(output_wav))

    logger.info(f"[yt] Converted to WAV: {wav_path}")

    return wav_path
