import sqlite3
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

# Zeabur Volume Path or Local fallback
DB_FOLDER = os.getenv("ZEABUR_VAR_DB_PATH", ".")
DB_PATH = os.path.join(DB_FOLDER, "360d.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            topic TEXT NOT NULL,
            summary TEXT,
            data_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT
        )
    ''')
    
    # Schedules Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            topic TEXT NOT NULL,
            email TEXT NOT NULL,
            frequency_days INTEGER NOT NULL,
            last_run DATETIME,
            next_run DATETIME,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migrations - Use helper to avoid repetition and indentation errors
    migrations = [
        "ALTER TABLE schedules ADD COLUMN url TEXT DEFAULT ''",
        "ALTER TABLE schedules ADD COLUMN topic TEXT DEFAULT ''",
        "ALTER TABLE schedules ADD COLUMN scraper_type TEXT DEFAULT 'AI'",
        "ALTER TABLE schedules ADD COLUMN unit TEXT DEFAULT 'days'",
        "ALTER TABLE schedules ADD COLUMN is_continuous BOOLEAN DEFAULT 1"
    ]
    
    for query in migrations:
        try:
            c.execute(query)
        except sqlite3.OperationalError:
            pass # Column likely exists
    
    conn.commit()
    conn.close()

def add_history(url: str, topic: str, data: List[Dict], status: str = "success"):
    conn = get_connection()
    c = conn.cursor()
    # Create a summary string (e.g., "Found 5 items")
    summary = f"Found {len(data)} items" if data else "No data found"
    
    c.execute(
        "INSERT INTO history (url, topic, summary, data_json, status) VALUES (?, ?, ?, ?, ?)",
        (url, topic, summary, json.dumps(data, ensure_ascii=False), status)
    )
    conn.commit()
    conn.close()

def get_history(limit: int = 50):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_last_history_for_url(url: str):
    """
    Retrieves the most recent history entry for a specific URL.
    Used for detecting duplicate manual checks.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE url = ? ORDER BY timestamp DESC LIMIT 1", (url,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def add_schedule(url: str, topic: str, email: str, frequency_days: int, scraper_type: str = "AI", unit: str = "days", is_continuous: bool = True):
    conn = get_connection()
    c = conn.cursor()
    
    # IMPORTANT: Deactivate any existing active schedule for the same URL+Email to prevent duplicates
    c.execute(
        "UPDATE schedules SET is_active = 0 WHERE url = ? AND email = ? AND is_active = 1",
        (url, email)
    )
    deactivated = c.rowcount
    if deactivated > 0:
        print(f"[DB] Deactivated {deactivated} existing schedule(s) for {url}")
    
    # Calculate next_run based on frequency and unit
    if unit == 'minutes':
        next_run_expr = f"datetime('now', '+{frequency_days} minutes')"
    else:
        next_run_expr = f"datetime('now', '+{frequency_days} days')"
    
    c.execute(
        f"INSERT INTO schedules (url, topic, email, frequency_days, scraper_type, unit, next_run, is_continuous) VALUES (?, ?, ?, ?, ?, ?, {next_run_expr}, ?)",
        (url, topic, email, frequency_days, scraper_type, unit, 1 if is_continuous else 0)
    )
    schedule_id = c.lastrowid
    conn.commit()
    conn.close()
    return schedule_id

def get_due_schedules():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE is_active = 1 AND next_run <= datetime('now')")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_schedule_next_run(schedule_id: int, flow_val: int, unit: str = "days"):
    conn = get_connection()
    c = conn.cursor()
    
    # If unit is 'minutes', add flow_val minutes.
    # Otherwise add flow_val days.
    
    if unit == 'minutes':
         time_expr = f"datetime('now', '+{flow_val} minutes')"
    else:
         # Default to days. 
         # Legacy test mode (flow_val=0 -> 1 minute) is replaced by explicit unit='minutes' usage.
         if flow_val == 0 and unit == 'days':
             # Keep fallback just in case for old calls, though frontend now sends unit='minutes'
             time_expr = "datetime('now', '+1 minute')"
         else:
             time_expr = f"datetime('now', '+{flow_val} days')"

    c.execute(
        f"UPDATE schedules SET last_run = datetime('now'), next_run = {time_expr} WHERE id = ?",
        (schedule_id,)
    )
    conn.commit()
    conn.close()

def toggle_schedule_active(schedule_id: int, is_active: bool):
    """Toggle the is_active status of a schedule."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE schedules SET is_active = ? WHERE id = ?",
        (1 if is_active else 0, schedule_id)
    )
    conn.commit()
    conn.close()

def get_active_schedules():
    """Get all active schedules."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE is_active = 1 ORDER BY next_run ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def deactivate_all_schedules():
    """Deactivate all schedules. Returns the number of schedules affected."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE schedules SET is_active = 0 WHERE is_active = 1")
    count = c.rowcount
    conn.commit()
    conn.close()
    return count
