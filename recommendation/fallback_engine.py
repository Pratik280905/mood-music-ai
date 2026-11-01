"""
Local Catalog Recommendation Engine.
Provides deterministic, offline music intelligence without requiring Spotify credentials.
"""

import csv
import math
from typing import List, Dict, Any, Optional
from config.settings import SONGS_CSV_PATH, ACTIVITIES
from utils.validators import clamp
from utils.logging_config import logger

class FallbackEngine:
    """Local song catalog loader and similarity ranker."""

    def __init__(self):
        self.songs: List[Dict[str, Any]] = []
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Loads songs from data/songs.csv into memory."""
        if not SONGS_CSV_PATH.exists():
            logger.error(f"Catalog file not found at: {SONGS_CSV_PATH}")
            self.songs = []
            return

        try:
            with open(SONGS_CSV_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.songs = []
                for row in reader:
                    self.songs.append({
                        "id": row["id"],
                        "title": row["title"],
                        "artist": row["artist"],
                        "genre": row["genre"],
                        "language": row["language"],
                        "emotion": row["emotion"],
                        "valence": float(row["valence"]),
                        "energy": float(row["energy"]),
                        "danceability": float(row["danceability"]),
                        "acousticness": float(row["acousticness"]),
                        "tempo": float(row["tempo"]),
                        "activities": [a.strip() for a in row["activities"].split(",")],
                        "spotify_url": row["spotify_url"],
                        "source": "local_fallback"
                    })
            logger.info(f"Loaded {len(self.songs)} songs into Local Catalog Engine.")
        except Exception as e:
            logger.error(f"Error loading songs CSV: {e}")
            self.songs = []

    def get_candidates(
        self,
        current_valence: float,
        current_energy: float,
        target_valence: float,
        target_energy: float,
        primary_emotion: str,
        activity: str = "Study",
        genre_filter: Optional[str] = None,
        language_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculates emotional proximity, activity congruency, and filter matches for all songs.
        """
        if not self.songs:
            self._load_catalog()

        candidates = []
        activity_profile = ACTIVITIES.get(activity, ACTIVITIES["Study"])
        favored_genres = activity_profile["favored_genres"]
        act_energy_min, act_energy_max = activity_profile["energy_range"]

        for song in self.songs:
            # Language filter
            if language_filter and language_filter.lower() != "all":
                if song["language"].lower() != language_filter.lower():
                    continue

            # Optional genre filter
            if genre_filter and genre_filter.lower() != "all":
                if song["genre"].lower() != genre_filter.lower():
                    continue

            # 1. Current Mood Proximity (Normalized Euclidean distance in 2D circumplex space)
            # Map valence [-1, 1] to [0, 1] for uniform Euclidean scaling
            nv_song = (song["valence"] + 1.0) / 2.0
            nv_curr = (current_valence + 1.0) / 2.0
            dist_curr = math.sqrt((nv_song - nv_curr) ** 2 + (song["energy"] - current_energy) ** 2)
            mood_match = clamp(1.0 - (dist_curr / 1.414), 0.1, 1.0)

            # Direct emotion tag match boost
            if song["emotion"] == primary_emotion:
                mood_match = min(1.0, mood_match + 0.15)

            # 2. Desired Mood Proximity (Target destination along emotional journey)
            nv_target = (target_valence + 1.0) / 2.0
            dist_target = math.sqrt((nv_song - nv_target) ** 2 + (song["energy"] - target_energy) ** 2)
            desired_mood_match = clamp(1.0 - (dist_target / 1.414), 0.1, 1.0)

            # 3. Context / Activity Match
            context_match = 0.50
            if activity in song["activities"]:
                context_match += 0.30
            if song["genre"] in favored_genres:
                context_match += 0.20
            if act_energy_min <= song["energy"] <= act_energy_max:
                context_match += 0.10
            context_match = clamp(context_match, 0.2, 1.0)

            candidates.append({
                **song,
                "mood_match": round(mood_match, 3),
                "desired_mood_match": round(desired_mood_match, 3),
                "context_match": round(context_match, 3)
            })

        return candidates

fallback_engine = FallbackEngine()