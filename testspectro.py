from fingerprint.spectrogram import generate_spectrogram
from fingerprint.peak_picker import find_peaks

spec = generate_spectrogram("test.wav")  # use any WAV
peaks = find_peaks(spec)

print("Total peaks:", len(peaks))

