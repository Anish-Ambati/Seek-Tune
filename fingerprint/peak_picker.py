# fingerprint/peak_picker.py

import numpy as np
from scipy.ndimage import maximum_filter
from utils import get_logger

logger = get_logger("peak_picker")


def find_peaks(spectrogram: np.ndarray, threshold_percentile: int = 98):
    """
    Find local maxima in the spectrogram.
    Only the strongest peaks are selected.

    Returns:
        List of (frequency_bin, time_bin) peak positions.
    """

    logger.info("Finding spectral peaks...")

    # Compute threshold based on percentile
    threshold = np.percentile(spectrogram, threshold_percentile)

    # Apply local maximum filter
    local_max = maximum_filter(spectrogram, size=(20, 20)) == spectrogram

    # Apply threshold mask
    detected_peaks = local_max & (spectrogram >= threshold)

    # Extract coordinates
    peaks = np.argwhere(detected_peaks)

    logger.info(f"Detected {len(peaks)} peaks")

    return peaks
