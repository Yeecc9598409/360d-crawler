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
    
    # Simple migration check for existing tables
    try:
        c.execute("ALTER TABLE schedules ADD COLUMN url TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass # Column likely exists
        
    try:
        c.execute("ALTER TABLE schedules ADD COLUMN topic TEXT DEFAULT ''")
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

def add_schedule(url: str, topic: str, email: str, frequency_days: int):
    conn = get_connection()
    c = conn.cursor()
    # Check if exists to avoid duplicates (optional, for now allow multiple)
    c.execute(
        "INSERT INTO schedules (url, topic, email, frequency_days, next_run) VALUES (?, ?, ?, ?, datetime('now'))",
        (url, topic, email, frequency_days)
    )
    conn.commit()
    conn.close()

def get_due_schedules():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE is_active = 1 AND next_run <= datetime('now')")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_schedule_next_run(schedule_id: int, days_offset: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        f"UPDATE schedules SET last_run = datetime('now'), next_run = datetime('now', '+{days_offset} days') WHERE id = ?",
        (schedule_id,)
    )
    conn.commit()
    conn.close()
