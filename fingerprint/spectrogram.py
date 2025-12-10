# fingerprint/spectrogram.py

import librosa
import numpy as np
from utils import get_logger

logger = get_logger("spectrogram")


def generate_spectrogram(file_path: str, sample_rate: int = 22050):
    """
    Load audio file and generate magnitude spectrogram.
    This mirrors the Go FFT processing step.
    """

    logger.info(f"Loading audio: {file_path}")

    # Load audio (mono)
    y, sr = librosa.load(file_path, sr=sample_rate, mono=True)

    logger.info(f"Audio loaded: {len(y)} samples @ {sr} Hz")

    # Short-Time Fourier Transform (STFT)
    stft = librosa.stft(y, n_fft=2048, hop_length=512)

    # Magnitude spectrogram
    spectrogram = np.abs(stft)

    logger.info(
        f"Spectrogram generated: freq_bins={spectrogram.shape[0]}, time_bins={spectrogram.shape[1]}"
    )

    return spectrogram
