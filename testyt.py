from downloader.youtube import download_youtube_audio

wav_path = download_youtube_audio(
    "https://www.youtube.com/shorts/7SF4VwLqb6w",  # replace with your URL
    title_hint="test_youtube_song"
)

print("WAV path:", wav_path)
