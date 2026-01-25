import sqlite3
import os

db_path = r"c:\Users\c3024\Documents\AI courses\Application project\360D 作品- 爬蟲網頁\360d.db"
print(f"DB Path: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")
print()

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT id, timestamp FROM history ORDER BY id DESC LIMIT 10")
rows = c.fetchall()
conn.close()

print("--- Last 10 History Records ---")
for row in rows:
    print(f"  ID {row['id']}: {row['timestamp']}")
