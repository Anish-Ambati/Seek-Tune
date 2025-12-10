# matcher/matcher.py

from collections import Counter
from pathlib import Path

from fingerprint.spectrogram import generate_spectrogram
from fingerprint.peak_picker import find_peaks
from fingerprint.hasher import generate_hashes
from db import init_db, get_fingerprints_by_hash, get_song_by_id
from utils import get_logger

logger = get_logger("matcher")


def match_song(file_path: str):
    """
    Full matching pipeline:
        clip.wav -> spectrogram -> peaks -> hashes
        hashes -> DB lookup -> time-offset voting -> best song

    Returns:
        {
          "song_id": int | None,
          "title": str,
          "artist": str,
          "score": int,
        }
    """

    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Clip file does not exist: {file_path}")

    logger.info(f"[matcher] Matching clip: {file_path}")

    # Make sure DB exists
    init_db()

    # 1) Spectrogram of the CLIP
    spec = generate_spectrogram(file_path)

    # 2) Peaks in the clip
    peaks = find_peaks(spec)

    # 3) Hashes for the clip (hash_value, offset_time_bin)
    query_hashes = generate_hashes(peaks)

    if not query_hashes:
        logger.warning("[matcher] No hashes generated from clip.")
        return {
            "song_id": None,
            "title": "No match",
            "artist": "",
            "score": 0,
        }

    logger.info(f"[matcher] Generated {len(query_hashes)} hashes for clip")

    # 4) Time-offset voting
    votes = Counter()

    for hash_value, offset_clip in query_hashes:
        # All fingerprints in DB that share this hash
        matches = get_fingerprints_by_hash(hash_value)

        for fp in matches:
            # fp.offset is the song's time bin, offset_clip is the clip's time bin
            delta = int(round(fp.offset - offset_clip))
            votes[(fp.song_id, delta)] += 1

    if not votes:
        logger.warning("[matcher] No matching hashes found in DB.")
        return {
            "song_id": None,
            "title": "No match",
            "artist": "",
            "score": 0,
        }

    # 5) Find the (song_id, delta) pair with the highest vote count
    (best_song_id, best_delta), best_votes = votes.most_common(1)[0]
    logger.info(
        f"[matcher] Best alignment: song_id={best_song_id}, delta={best_delta}, votes={best_votes}"
    )

    # Aggregate total votes per song (sum over deltas)
    per_song_votes = Counter()
    for (song_id, _delta), count in votes.items():
        per_song_votes[song_id] += count

    final_song_id, final_score = per_song_votes.most_common(1)[0]

    song = get_song_by_id(final_song_id)

    if song is None:
        logger.error(f"[matcher] Song with id={final_song_id} not found in DB.")
        return {
            "song_id": final_song_id,
            "title": "Unknown Song",
            "artist": "",
            "score": final_score,
        }

    logger.info(
        f"[matcher] Final prediction: '{song.title}' by '{song.artist}' (score={final_score})"
    )

    return {
        "song_id": final_song_id,
        "title": song.title,
        "artist": song.artist,
        "score": final_score,
    }
