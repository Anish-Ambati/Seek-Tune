# main.py

import sys
import argparse
from pathlib import Path
import shutil

from config import (
    SONGS_DIR,
    RECORDINGS_DIR,
    TMP_DIR,
    DB_DIR,
    DEFAULT_PROTO,
    DEFAULT_PORT,
)
from utils import create_folder, get_logger
from fingerprint import generate_fingerprint
from matcher import match_song
from db import delete_db
from downloader.service import download_and_fingerprint_from_spotify

logger = get_logger("seek_tune_cli")


# -------------------------------------------------
# COMMAND IMPLEMENTATIONS
# -------------------------------------------------

def cmd_find(path: str):
    p = Path(path)
    if not p.exists():
        logger.error(f"[find] File does not exist: {path}")
        return

    logger.info(f"[find] Matching clip: {path}")
    result = match_song(str(p))

    if result["song_id"] is None or result["score"] == 0:
        print("No match found.")
    else:
        print(
            f"Prediction: '{result['title']}' by '{result['artist']}' "
            f"(score={result['score']})"
        )


def cmd_download(url: str):
    logger.info(f"[download] Spotify URL: {url}")

    try:
        result = download_and_fingerprint_from_spotify(url)

        print(
            f"Downloaded and saved: '{result['title']}' by '{result['artist']}' "
            f"(song_id={result['song_id']}, hashes={result['hashes']})"
        )
        print(f"WAV file: {result['wav_path']}")
    except Exception as e:
        logger.error(f"[download] Error: {e}")
        print(f"Error in download pipeline: {e}")



def cmd_save(path: str, force: bool):
    p = Path(path)
    if not p.exists():
        logger.error(f"[save] Path does not exist: {path}")
        return

    logger.info(f"[save] Saving from path: {path}")
    logger.info(f"[save] Force mode: {force}")

    # For now, we ignore 'force' logic (YouTube ID etc.) and just fingerprint
    # local audio files. Later we can add metadata/Spotify logic like the Go repo.

    audio_exts = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}

    def process_file(file_path: Path):
        if file_path.suffix.lower() not in audio_exts:
            logger.info(f"[save] Skipping non-audio file: {file_path}")
            return

        logger.info(f"[save] Fingerprinting file: {file_path}")
        try:
            song_id, num_hashes = generate_fingerprint(str(file_path))
            logger.info(
                f"[save] OK: song_id={song_id}, hashes={num_hashes} "
                f"({file_path.name})"
            )
            print(
                f"Saved: '{file_path.name}' (song_id={song_id}, hashes={num_hashes})"
            )
        except Exception as e:
            logger.error(f"[save] Error processing {file_path}: {e}")

    if p.is_dir():
        # Walk directory and process all audio files
        for file_path in p.rglob("*"):
            if file_path.is_file():
                process_file(file_path)
    else:
        process_file(p)


def cmd_erase(db_only: bool, all_: bool):
    if all_:
        logger.info("[erase] Deleting database + songs + recordings")

        # Delete DB
        delete_db()

        # Delete songs and recordings
        for folder in (SONGS_DIR, RECORDINGS_DIR):
            if folder.exists():
                shutil.rmtree(folder)
                logger.info(f"[erase] Deleted folder: {folder}")
            create_folder(folder)

        print("Database and audio folders erased.")
    else:
        logger.info("[erase] Deleting only database")
        delete_db()
        print("Database erased.")


def cmd_serve(proto: str, port: int):
    logger.info(f"[serve] Starting server on {proto}://0.0.0.0:{port}")

    import uvicorn
    from api import app

    # For now we ignore HTTPS; proto is kept for similarity with Go
    uvicorn.run(app, host="0.0.0.0", port=port)



# -------------------------------------------------
# MAIN CLI ROUTER
# -------------------------------------------------

def main():
    # Ensure required folders exist (same as Go utils.CreateFolder)
    create_folder(SONGS_DIR)
    create_folder(RECORDINGS_DIR)
    create_folder(TMP_DIR)
    create_folder(DB_DIR)

    if len(sys.argv) < 2:
        print("Expected 'find', 'download', 'erase', 'save', or 'serve' subcommands\n")
        print("Usage examples:")
        print("  python main.py find <path_to_wav_file>")
        print("  python main.py download <spotify_url>")
        print("  python main.py erase [db | all]  (default: db)")
        print("  python main.py save [-f|--force] <path_to_file_or_dir>")
        print("  python main.py serve [--proto <http|https>] [--port <port>]")
        sys.exit(1)

    cmd = sys.argv[1]

    # ---------------- FIND ----------------
    if cmd == "find":
        if len(sys.argv) < 3:
            print("Usage: python main.py find <path_to_wav_file>")
            sys.exit(1)

        file_path = sys.argv[2]
        cmd_find(file_path)

    # ---------------- DOWNLOAD ----------------
    elif cmd == "download":
        if len(sys.argv) < 3:
            print("Usage: python main.py download <spotify_url>")
            sys.exit(1)

        url = sys.argv[2]
        cmd_download(url)

    # ---------------- SAVE ----------------
    elif cmd == "save":
        parser = argparse.ArgumentParser(prog="python main.py save")
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="Save even if metadata or YouTube ID is missing"
        )
        parser.add_argument(
            "path",
            help="Path to a song file or directory of songs"
        )
        args = parser.parse_args(sys.argv[2:])

        cmd_save(args.path, args.force)

    # ---------------- ERASE ----------------
    elif cmd == "erase":
        db_only = True
        all_ = False

        if len(sys.argv) > 2:
            mode = sys.argv[2].lower()
            if mode == "db":
                db_only = True
                all_ = False
            elif mode == "all":
                db_only = False
                all_ = True
            else:
                print("Usage: python main.py erase [db | all]")
                sys.exit(1)

        cmd_erase(db_only, all_)

    # ---------------- SERVE ----------------
    elif cmd == "serve":
        parser = argparse.ArgumentParser(prog="python main.py serve")
        parser.add_argument(
            "--proto",
            default=DEFAULT_PROTO,
            choices=["http", "https"],
            help="Protocol to use"
        )
        parser.add_argument(
            "--port", "-p",
            default=DEFAULT_PORT,
            type=int,
            help="Port number"
        )
        args = parser.parse_args(sys.argv[2:])

        cmd_serve(args.proto, args.port)

    else:
        print("Expected 'find', 'download', 'erase', 'save', or 'serve' subcommands\n")
        print("Usage examples:")
        print("  python main.py find <path_to_wav_file>")
        print("  python main.py download <spotify_url>")
        print("  python main.py erase [db | all]  (default: db)")
        print("  python main.py save [-f|--force] <path_to_file_or_dir>")
        print("  python main.py serve [--proto <http|https>] [--port <port>]")
        sys.exit(1)


if __name__ == "__main__":
    main()
