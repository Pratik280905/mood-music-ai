"""
Resilient Spotify API Service Integration.
Adheres strictly to Spotify's Non-Premium restrictions: uses only public search/metadata
discovery when authorized, and falls back gracefully with structured statuses.
"""

from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from utils.logging_config import logger

class SpotifyService:
    """
    Handles Spotify API interactions with automatic error recovery and local fallback switching.
    """

    def __init__(self):
        self.client = None
        self.is_connected = False
        self.init_error: Optional[str] = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Attempts Client Credentials authentication if valid secrets are present."""
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            self.is_connected = False
            self.init_error = "Spotify API credentials not provided in .env."
            logger.info(self.init_error)
            return

        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials

            auth_manager = SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            )
            self.client = spotipy.Spotify(
                auth_manager=auth_manager,
                requests_timeout=5,
                retries=1
            )
            # Test connection with a lightweight search
            self.client.search(q="test", limit=1, type="track")
            self.is_connected = True
            self.init_error = None
            logger.info("Successfully connected to Spotify Web API (Client Credentials mode).")
        except Exception as e:
            self.client = None
            self.is_connected = False
            self.init_error = f"Spotify authentication error: {str(e)}"
            logger.warning(f"Spotify authentication failed: {e}. Switching to Local AI Fallback Engine.")

    def search_tracks(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Searches Spotify catalog for matching tracks using public search endpoint.
        Returns a structured dictionary indicating success, source, and tracks.
        """
        if not self.is_connected or self.client is None:
            return {
                "success": False,
                "source": "local_fallback",
                "error": self.init_error or "Spotify service is disconnected.",
                "tracks": []
            }

        try:
            res = self.client.search(q=query, limit=limit, type="track")
            items = res.get("tracks", {}).get("items", [])
            tracks = []

            for item in items:
                track_id = item.get("id", "")
                name = item.get("name", "Unknown Track")
                artists = ", ".join([a.get("name", "") for a in item.get("artists", [])])
                spotify_url = item.get("external_urls", {}).get("spotify") or f"https://open.spotify.com/track/{track_id}"
                album_art = None
                images = item.get("album", {}).get("images", [])
                if images:
                    album_art = images[0].get("url")

                tracks.append({
                    "id": track_id,
                    "title": name,
                    "artist": artists,
                    "genre": "Spotify Discovery",
                    "spotify_url": spotify_url,
                    "album_art": album_art,
                    "source": "spotify"
                })

            logger.info(f"Spotify search for '{query}' returned {len(tracks)} tracks.")
            return {
                "success": True,
                "source": "spotify",
                "error": None,
                "tracks": tracks
            }

        except Exception as e:
            err_msg = f"Spotify API request error: {str(e)}"
            logger.warning(f"{err_msg}. Seamlessly falling back to local catalog.")
            return {
                "success": False,
                "source": "local_fallback",
                "error": err_msg,
                "tracks": []
            }

    @staticmethod
    def get_search_url(query: str) -> str:
        """Returns a direct Spotify web search link for an arbitrary song query."""
        encoded = quote_plus(query)
        return f"https://open.spotify.com/search/{encoded}"

# Singleton instance
spotify_service = SpotifyService()