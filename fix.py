import sqlite3

filename = "/storage/emulated/0/AnkiDroid/collection.anki2"
conn = sqlite3.connect(filename)
conn.execute("PRAGMA wal_checkpoint(RESTART)")
conn.commit()
conn.close()
