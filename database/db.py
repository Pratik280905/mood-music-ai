"""
SQLite Database Connection and Schema Management.
"""

import sqlite3
from typing import Generator
from contextlib import contextmanager
from config.settings import DB_PATH, DATABASE_DIR
from utils.logging_config import logger

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection configured with row factory and foreign keys."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for safely executing queries and committing transactions."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db() -> None:
    """Creates database tables if they do not exist."""
    with get_db_cursor() as cur:
        # 1. Users Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # 2. Mood Sessions Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mood_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                text_input TEXT,
                has_face INTEGER DEFAULT 0,
                text_emotion TEXT,
                face_emotion TEXT,
                fused_emotion TEXT NOT NULL,
                intensity REAL DEFAULT 0.5,
                valence REAL DEFAULT 0.0,
                energy REAL DEFAULT 0.5,
                strategy TEXT DEFAULT 'Match My Mood',
                activity TEXT DEFAULT 'Study',
                context_json TEXT
            )
        """)

        # 3. Recommendations Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                song_id TEXT NOT NULL,
                song_title TEXT NOT NULL,
                artist TEXT NOT NULL,
                genre TEXT,
                score REAL NOT NULL,
                source TEXT DEFAULT 'local_fallback',
                why_json TEXT,
                spotify_url TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES mood_sessions(id) ON DELETE CASCADE
            )
        """)

        # 4. Feedback Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id TEXT NOT NULL,
                song_title TEXT NOT NULL,
                artist TEXT NOT NULL,
                genre TEXT,
                action TEXT NOT NULL,
                mood TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        # 5. User Preferences Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                user_id TEXT PRIMARY KEY,
                genre_weights_json TEXT DEFAULT '{}',
                artist_weights_json TEXT DEFAULT '{}',
                valence_pref REAL DEFAULT 0.0,
                energy_pref REAL DEFAULT 0.5,
                updated_at TEXT NOT NULL
            )
        """)

        # Insert default user if missing
        cur.execute("""
            INSERT OR IGNORE INTO users (id, username, created_at)
            VALUES ('default_user', 'MoodMuse Listener', datetime('now'))
        """)

    logger.info("Database schema initialized successfully.")

# Run initialization on import
init_db()