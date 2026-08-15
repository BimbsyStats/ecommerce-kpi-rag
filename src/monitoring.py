import os
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR =Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getcwd()) / "feedback.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH.resolve()))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            engine TEXT,
            rating INTEGER,
            response_time_ms REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_interaction(question, answer, engine, rating=None, response_time_ms=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
    """INSERT INTO feedback
        (question, answer, engine, rating, response_time_ms, timestamp)
         VALUES (?, ?, ?, ?, ?, ?)""",
(question, answer, engine, rating, response_time_ms, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()

def get_all_feedback():
    import pandas as pd
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_db()
print(f"Initialized feedback DB at {DB_PATH}")