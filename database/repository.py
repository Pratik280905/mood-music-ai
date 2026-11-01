"""
Database repository providing clean CRUD operations for MoodMuse AI.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from database.db import get_db_cursor
from database.models import MoodSessionRecord, RecommendationRecord, FeedbackRecord, UserPreferencesRecord
from utils.logging_config import logger

class MoodRepository:
    """Repository handling all database operations."""

    @staticmethod
    def create_mood_session(record: MoodSessionRecord) -> int:
        """Inserts a new mood session and returns its ID."""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO mood_sessions (
                    timestamp, text_input, has_face, text_emotion, face_emotion,
                    fused_emotion, intensity, valence, energy, strategy, activity, context_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.timestamp,
                record.text_input,
                1 if record.has_face else 0,
                record.text_emotion,
                record.face_emotion,
                record.fused_emotion,
                record.intensity,
                record.valence,
                record.energy,
                record.strategy,
                record.activity,
                record.context_json
            ))
            session_id = cur.lastrowid
            logger.info(f"Created MoodSession id: {session_id} for emotion: {record.fused_emotion}")
            return session_id

    @staticmethod
    def save_recommendations(session_id: int, recommendations: List[Dict[str, Any]]) -> None:
        """Saves a batch of generated recommendations for a session."""
        with get_db_cursor() as cur:
            for rec in recommendations:
                cur.execute("""
                    INSERT INTO recommendations (
                        session_id, song_id, song_title, artist, genre, score,
                        source, why_json, spotify_url, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    str(rec.get("id", "")),
                    str(rec.get("title", "")),
                    str(rec.get("artist", "")),
                    str(rec.get("genre", "")),
                    float(rec.get("score", 0.0)),
                    str(rec.get("source", "local_fallback")),
                    json.dumps(rec.get("explanation", {})),
                    str(rec.get("spotify_url", "")),
                    datetime.now().isoformat(timespec="seconds")
                ))

    @staticmethod
    def record_feedback(
        song_id: str,
        song_title: str,
        artist: str,
        genre: str,
        action: str,
        mood: str = "neutral"
    ) -> None:
        """Records user interaction (liked, disliked, skipped, opened_external)."""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO feedback (song_id, song_title, artist, genre, action, mood, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                song_id,
                song_title,
                artist,
                genre,
                action,
                mood,
                datetime.now().isoformat(timespec="seconds")
            ))
            logger.info(f"Recorded feedback: '{action}' on '{song_title}' by '{artist}'")

    @staticmethod
    def get_mood_sessions(limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent mood sessions sorted newest first."""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM mood_sessions
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_liked_songs() -> List[Dict[str, Any]]:
        """Retrieves all songs currently liked by the user."""
        with get_db_cursor() as cur:
            # Get latest action per song
            cur.execute("""
                SELECT f.song_id, f.song_title, f.artist, f.genre, f.mood, f.timestamp
                FROM feedback f
                INNER JOIN (
                    SELECT song_id, MAX(id) as max_id
                    FROM feedback
                    WHERE action IN ('liked', 'disliked')
                    GROUP BY song_id
                ) latest ON f.id = latest.max_id
                WHERE f.action = 'liked'
                ORDER BY f.id DESC
            """)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_feedback_summary() -> Dict[str, Any]:
        """Calculates aggregated metrics for likes, dislikes, skips, and top genres."""
        with get_db_cursor() as cur:
            cur.execute("SELECT action, COUNT(*) as count FROM feedback GROUP BY action")
            action_counts = {r["action"]: r["count"] for r in cur.fetchall()}

            cur.execute("""
                SELECT genre, COUNT(*) as count
                FROM feedback
                WHERE action = 'liked' AND genre != ''
                GROUP BY genre
                ORDER BY count DESC
                LIMIT 5
            """)
            top_genres = [(r["genre"], r["count"]) for r in cur.fetchall()]

            cur.execute("""
                SELECT artist, COUNT(*) as count
                FROM feedback
                WHERE action = 'liked' AND artist != ''
                GROUP BY artist
                ORDER BY count DESC
                LIMIT 5
            """)
            top_artists = [(r["artist"], r["count"]) for r in cur.fetchall()]

            return {
                "action_counts": action_counts,
                "likes": action_counts.get("liked", 0),
                "dislikes": action_counts.get("disliked", 0),
                "skips": action_counts.get("skipped", 0),
                "opened": action_counts.get("opened_external", 0),
                "top_genres": top_genres,
                "top_artists": top_artists
            }

    @staticmethod
    def get_user_preferences(user_id: str = "default_user") -> UserPreferencesRecord:
        """Loads learned preferences for a user."""
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM preferences WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if not row:
                return UserPreferencesRecord(user_id=user_id)
            return UserPreferencesRecord(
                user_id=row["user_id"],
                genre_weights=json.loads(row["genre_weights_json"] or "{}"),
                artist_weights=json.loads(row["artist_weights_json"] or "{}"),
                valence_pref=row["valence_pref"] if row["valence_pref"] is not None else 0.0,
                energy_pref=row["energy_pref"] if row["energy_pref"] is not None else 0.5,
                updated_at=row["updated_at"]
            )

    @staticmethod
    def update_user_preferences(prefs: UserPreferencesRecord) -> None:
        """Persists updated preference weights."""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO preferences (
                    user_id, genre_weights_json, artist_weights_json,
                    valence_pref, energy_pref, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    genre_weights_json = excluded.genre_weights_json,
                    artist_weights_json = excluded.artist_weights_json,
                    valence_pref = excluded.valence_pref,
                    energy_pref = excluded.energy_pref,
                    updated_at = excluded.updated_at
            """, (
                prefs.user_id,
                json.dumps(prefs.genre_weights),
                json.dumps(prefs.artist_weights),
                prefs.valence_pref,
                prefs.energy_pref,
                datetime.now().isoformat(timespec="seconds")
            ))

    @staticmethod
    def reset_all_data() -> None:
        """Clears all session logs, feedback, and custom preferences."""
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM recommendations")
            cur.execute("DELETE FROM mood_sessions")
            cur.execute("DELETE FROM feedback")
            cur.execute("DELETE FROM preferences")
        logger.info("All user database records reset.")