import sqlite3

# Check 360d.db (the actual database used by database.py)
db_file = '360d.db'
print(f"=== Checking {db_file} ===")

conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# List all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)

# Check schedules
if 'schedules' in tables:
    c.execute("SELECT id, url, email, is_active, next_run, frequency_days, unit FROM schedules")
    rows = c.fetchall()
    print(f"\nFound {len(rows)} schedules:")
    for row in rows:
        print(dict(row))
    
    # Count active ones
    c.execute("SELECT COUNT(*) FROM schedules WHERE is_active = 1")
    active_count = c.fetchone()[0]
    print(f"\nActive schedules: {active_count}")
    
    # Deactivate all schedules
    print("\n--- Deactivating ALL schedules ---")
    c.execute("UPDATE schedules SET is_active = 0")
    conn.commit()
    print(f"Deactivated {c.rowcount} schedules")
else:
    print("No schedules table")

conn.close()
print("\nDone! All schedules have been stopped.")
