"""
Spotify Recommendation Adapter.
Queries Spotify search endpoints when credentials are valid, formatting results
into standard candidates for ranking, or returning fallback signals upon restriction.
"""

from typing import List, Dict, Any, Optional
from services.spotify_service import spotify_service
from utils.logging_config import logger

class SpotifyEngine:
    """Wrapper that delegates discovery queries to SpotifyService."""

    def __init__(self):
        self.service = spotify_service

    def get_candidates(
        self,
        primary_emotion: str,
        activity: str,
        genre_filter: Optional[str] = None,
        limit: int = 15
    ) -> Dict[str, Any]:
        """
        Attempts to search Spotify catalog using emotion + context terms.
        Returns {"source": "spotify" | "local_fallback", "tracks": [...], "error": ...}
        """
        if not self.service.is_connected:
            return {
                "source": "local_fallback",
                "tracks": [],
                "error": self.service.init_error or "Spotify credentials not active."
            }

        # Formulate query
        parts = [primary_emotion]
        if genre_filter and genre_filter.lower() != "all":
            parts.append(f"genre:{genre_filter.lower()}")
        elif activity:
            parts.append(activity)

        query = " ".join(parts)
        result = self.service.search_tracks(query=query, limit=limit)

        if not result.get("success") or not result.get("tracks"):
            return {
                "source": "local_fallback",
                "tracks": [],
                "error": result.get("error") or "No tracks returned from Spotify search."
            }

        return {
            "source": "spotify",
            "tracks": result.get("tracks", []),
            "error": None
        }

spotify_engine = SpotifyEngine()