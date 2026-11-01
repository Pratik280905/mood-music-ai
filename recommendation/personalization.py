"""
Online User Preference Learning and Taste Profile Personalization.
Dynamically adapts user genre affinity, artist weights, and emotional center based on interactions.
"""

from typing import Dict, Any, Set
from database.repository import MoodRepository
from utils.validators import clamp
from utils.logging_config import logger

class PersonalizationEngine:
    """Handles online reinforcement of music taste based on like/skip/dislike feedback."""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self._load_state()

    def _load_state(self) -> None:
        """Loads learned weights and feedback history from SQLite."""
        self.pref_record = MoodRepository.get_user_preferences(self.user_id)
        self.genre_weights = self.pref_record.genre_weights
        self.artist_weights = self.pref_record.artist_weights
        self.valence_pref = self.pref_record.valence_pref
        self.energy_pref = self.pref_record.energy_pref

        # Load interacted song IDs
        summary = MoodRepository.get_feedback_summary()
        liked_songs = MoodRepository.get_liked_songs()
        self.liked_ids = {s["song_id"] for s in liked_songs}

    def process_feedback(self, song: Dict[str, Any], action: str, mood: str = "neutral") -> None:
        """
        Updates preference state when user interacts with a song.

        Actions:
            - 'liked': Strong positive reinforcement (+0.30 artist, +0.20 genre, taste shift)
            - 'disliked': Negative penalty (-0.40 artist, -0.25 genre)
            - 'skipped': Mild penalty (-0.15 genre)
            - 'opened_external': Positive signal (+0.20 artist, +0.10 genre)
        """
        song_id = str(song.get("id", ""))
        title = song.get("title", "")
        artist = song.get("artist", "").strip()
        genre = song.get("genre", "").strip()
        s_val = float(song.get("valence", 0.0))
        s_eng = float(song.get("energy", 0.5))

        # Record event in SQLite
        MoodRepository.record_feedback(
            song_id=song_id,
            song_title=title,
            artist=artist,
            genre=genre,
            action=action,
            mood=mood
        )

        # Update weights
        if action == "liked":
            self.artist_weights[artist] = round(self.artist_weights.get(artist, 0.0) + 0.35, 3)
            self.genre_weights[genre] = round(self.genre_weights.get(genre, 0.0) + 0.25, 3)
            self.liked_ids.add(song_id)
            # Adapt taste coordinates
            self.valence_pref = round((0.85 * self.valence_pref) + (0.15 * s_val), 3)
            self.energy_pref = round((0.85 * self.energy_pref) + (0.15 * s_eng), 3)

        elif action == "disliked":
            self.artist_weights[artist] = round(self.artist_weights.get(artist, 0.0) - 0.40, 3)
            self.genre_weights[genre] = round(self.genre_weights.get(genre, 0.0) - 0.25, 3)
            self.liked_ids.discard(song_id)

        elif action == "skipped":
            self.genre_weights[genre] = round(self.genre_weights.get(genre, 0.0) - 0.12, 3)

        elif action == "opened_external":
            self.artist_weights[artist] = round(self.artist_weights.get(artist, 0.0) + 0.20, 3)
            self.genre_weights[genre] = round(self.genre_weights.get(genre, 0.0) + 0.10, 3)

        # Persist to database
        self.pref_record.genre_weights = self.genre_weights
        self.pref_record.artist_weights = self.artist_weights
        self.pref_record.valence_pref = self.valence_pref
        self.pref_record.energy_pref = self.energy_pref
        MoodRepository.update_user_preferences(self.pref_record)

        logger.info(f"Updated taste profile for user '{self.user_id}' after '{action}'")

    def calculate_preference_score(self, song: Dict[str, Any]) -> float:
        """
        Computes song alignment with the user's learned profile in [0.1, 1.0].
        """
        artist = song.get("artist", "").strip()
        genre = song.get("genre", "").strip()

        artist_boost = self.artist_weights.get(artist, 0.0)
        genre_boost = self.genre_weights.get(genre, 0.0)

        # Baseline alignment is 0.50 (neutral)
        raw_score = 0.50 + (0.30 * artist_boost) + (0.25 * genre_boost)

        # Proximity to preferred valence/energy
        s_val = float(song.get("valence", 0.0))
        s_eng = float(song.get("energy", 0.5))
        diff = ((s_val - self.valence_pref) ** 2 + (s_eng - self.energy_pref) ** 2) ** 0.5
        taste_proximity = 1.0 - (diff / 1.414)
        raw_score = (0.70 * raw_score) + (0.30 * taste_proximity)

        return round(clamp(raw_score, 0.10, 0.98), 3)

    def calculate_novelty_score(self, song: Dict[str, Any]) -> float:
        """Songs already liked or heavily interacted with have lower novelty."""
        song_id = str(song.get("id", ""))
        if song_id in self.liked_ids:
            return 0.35  # Familiar favorite
        artist = song.get("artist", "").strip()
        if self.artist_weights.get(artist, 0.0) > 0.3:
            return 0.65  # Familiar artist
        return 0.92  # Fresh discovery

personalization_engine = PersonalizationEngine()