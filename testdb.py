from db import init_db, insert_song, insert_fingerprints, get_fingerprints_by_hash

init_db()

song_id = insert_song("Test Song", "Test Artist", "/tmp/test.wav")

insert_fingerprints(song_id, [
    ("hash1", 0.1),
    ("hash2", 0.2),
])

matches = get_fingerprints_by_hash("hash1")
print("Matches:", matches)
