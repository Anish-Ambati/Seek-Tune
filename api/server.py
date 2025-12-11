# api/server.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from config import SONGS_DIR, RECORDINGS_DIR
from utils import create_folder, get_logger
from fingerprint import generate_fingerprint
from matcher import match_song
from fastapi.middleware.cors import CORSMiddleware
from downloader.service import download_and_fingerprint_from_spotify
from db.sqlite import get_song_by_id
from fastapi import Body

logger = get_logger("api")

app = FastAPI(title="SeekTune Python API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/save")
async def save_song_api(file: UploadFile = File(...)):
    """
    Save a full song via HTTP upload.
    Equivalent to: python main.py save <file>
    """
    create_folder(SONGS_DIR)

    target_path = SONGS_DIR / file.filename

    # Save uploaded file to disk
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"[API/save] Saved uploaded file to: {target_path}")

    try:
        # generate_fingerprint accepts optional spotify_url / youtube_url (None here)
        song_id, num_hashes = generate_fingerprint(str(target_path))

        # fetch song row to return any stored links (if available)
        song = get_song_by_id(song_id)

        return {
            "status": "ok",
            "song_id": song_id,
            "hashes": num_hashes,
            "filename": file.filename,
            "spotify_url": getattr(song, "spotify_url", None),
            "youtube_url": getattr(song, "youtube_url", None),
        }
    except Exception as e:
        logger.error(f"[API/save] Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
        )
    

@app.post("/api/find")
async def find_song_api(file: UploadFile = File(...)):
    """
    Match a short clip via HTTP upload.
    Equivalent to: python main.py find <clip.wav>
    """
    create_folder(RECORDINGS_DIR)

    target_path = RECORDINGS_DIR / file.filename

    # Save uploaded clip
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"[API/find] Saved uploaded clip to: {target_path}")

    try:
        result = match_song(str(target_path))

        # result should contain 'song_id', 'title', 'artist', 'score'
        song_obj = get_song_by_id(result["song_id"])

        logger.info(f"[API/find] Returning prediction for song_id={result['song_id']} spotify={getattr(song_obj,'spotify_url',None)} youtube={getattr(song_obj,'youtube_url',None)}")

        return {
            "status": "ok",
            "prediction": {
                "song_id": result["song_id"],
                "title": result["title"],
                "artist": result["artist"],
                "score": result.get("score"),
                "spotify_url": getattr(song_obj, "spotify_url", None),
                "youtube_url": getattr(song_obj, "youtube_url", None),
            },
        }
    except Exception as e:
        logger.error(f"[API/find] Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
        )

@app.post("/api/download")
async def download_from_spotify_api(payload: dict = Body(...)):
    """
    Download + fingerprint a song from a Spotify track URL.
    """
    try:
        spotify_url = payload.get("spotify_url")
        if not spotify_url:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "detail": "spotify_url is required"},
            )

        result = download_and_fingerprint_from_spotify(spotify_url)

        return {
            "status": "ok",
            "song_id": result["song_id"],
            "title": result["title"],
            "artist": result["artist"],
            "hashes": result["hashes"],
            "wav_path": result["wav_path"],
            "spotify_url": result.get("spotify_url"),
            "youtube_url": result.get("youtube_url"),
        }


    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
        )
