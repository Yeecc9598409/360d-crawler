import sqlite3
import os

DB_PATH = "360d.db"

def check_db():
    if not os.path.exists(DB_PATH):
        print("DB not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("PRAGMA table_info(schedules)")
        columns = [row[1] for row in c.fetchall()]
        print(f"Columns in schedules: {columns}")
        
        if 'unit' in columns:
            print("SUCCESS: 'unit' column exists.")
        else:
            print("FAILURE: 'unit' column MISSING.")
            
        # Check active schedules
        c.execute("SELECT * FROM schedules")
        rows = c.fetchall()
        print(f"Total schedules: {len(rows)}")
        for r in rows:
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
