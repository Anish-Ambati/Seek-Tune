# fingerprint/hasher.py

import numpy as np
import hashlib
from utils import get_logger

logger = get_logger("hasher")

# How many future peaks to pair with each anchor peak
FAN_VALUE = 10

# Min and max time difference between anchor and target peaks (in frames)
MIN_TIME_DELTA = 1
MAX_TIME_DELTA = 200


def generate_hashes(peaks: np.ndarray):
    """
    Generate Shazam-style hashes from a list/array of peaks.

    peaks: np.ndarray of shape (N, 2), each row = [freq_bin, time_bin]

    Returns:
        List of (hash_value, offset_time_bin)
    """

    logger.info("Generating hashes from peaks...")

    # Ensure peaks is a numpy array
    peaks = np.asarray(peaks)

    if peaks.shape[0] == 0:
        logger.warning("No peaks provided, returning empty hash list.")
        return []

    hashes = []

    # Sort peaks by time for consistency
    # peaks[:, 0] = freq, peaks[:, 1] = time (assuming that order)
    # If you used (time, freq) earlier, just swap indexing.
    # Here we'll assume (freq, time) as in our peak_picker output.
    peaks = peaks[np.argsort(peaks[:, 1])]

    num_peaks = peaks.shape[0]

    for i in range(num_peaks):
        f1, t1 = peaks[i]

        # Pair this anchor with the next FAN_VALUE peaks
        for j in range(1, FAN_VALUE + 1):
            if i + j >= num_peaks:
                break

            f2, t2 = peaks[i + j]
            dt = t2 - t1

            # Only consider pairs within allowed time range
            if dt < MIN_TIME_DELTA or dt > MAX_TIME_DELTA:
                continue

            # Create hash string
            hash_str = f"{int(f1)}|{int(f2)}|{int(dt)}"

            # SHA1 hash for compactness
            hash_value = hashlib.sha1(hash_str.encode("utf-8")).hexdigest()

            # Offset = time of anchor peak
            hashes.append((hash_value, int(t1)))

    logger.info(f"Generated {len(hashes)} hashes from {num_peaks} peaks")

    return hashes
