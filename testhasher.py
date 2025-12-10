from fingerprint import generate_fingerprint

song_id, num_hashes = generate_fingerprint("test.wav")

print("Song ID:", song_id)
print("Total hashes:", num_hashes)
