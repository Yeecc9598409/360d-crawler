import scheduler
import database
import time

def test_run():
    print("Testing scheduler run...")
    database.init_db()
    
    # Ensure there is a due job (the one we just added in debug_add_schedule.py might be due now or soon)
    # Check current schedules
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM schedules")
    rows = c.fetchall()
    print(f"Current Schedules: {len(rows)}")
    for r in rows:
        print(dict(r))
    conn.close()

    print("Running check_and_run_jobs()...")
    try:
        scheduler.check_and_run_jobs()
        print("Scheduler run finish.")
    except Exception as e:
        print(f"SCHEDULER CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
