import sqlite3

for db_file in ['scraper_history.db', '360d.db']:
    print(f"\n=== Checking {db_file} ===")
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # List all tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]
        print("Tables:", tables)

        # Check schedules
        if 'schedules' in tables:
            c.execute("SELECT * FROM schedules")
            rows = c.fetchall()
            print(f"Found {len(rows)} schedules:")
            for row in rows:
                print(dict(row))
        else:
            print("No schedules table")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")
