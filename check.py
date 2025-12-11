from db.sqlite import SessionLocal, Song, get_song_by_id
s = get_song_by_id(4)   # try id 1, 2, etc.
print("title:", s.title)
print("spotify_url:", s.spotify_url)
print("youtube_url:", s.youtube_url)
