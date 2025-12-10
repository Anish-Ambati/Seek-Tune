import librosa
import soundfile as sf

y, sr = librosa.load("test.wav", sr=None)

start = int(5 * sr)
end = int(8 * sr)

clip = y[start:end]

sf.write("clip.wav", clip, sr)
print("clip.wav created!")
