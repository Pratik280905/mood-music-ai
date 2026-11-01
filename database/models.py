"""
Data models and dataclasses for MoodMuse AI persistence.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class MoodSessionRecord:
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    text_input: str = ""
    has_face: bool = False
    text_emotion: str = "neutral"
    face_emotion: str = "neutral"
    fused_emotion: str = "neutral"
    intensity: float = 0.5
    valence: float = 0.0
    energy: float = 0.5
    strategy: str = "Match My Mood"
    activity: str = "Study"
    context_json: str = "{}"

@dataclass
class RecommendationRecord:
    id: Optional[int] = None
    session_id: Optional[int] = None
    song_id: str = ""
    song_title: str = ""
    artist: str = ""
    genre: str = ""
    score: float = 0.0
    source: str = "local_fallback"
    why_json: str = "{}"
    spotify_url: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

@dataclass
class FeedbackRecord:
    id: Optional[int] = None
    song_id: str = ""
    song_title: str = ""
    artist: str = ""
    genre: str = ""
    action: str = "liked"  # liked, disliked, skipped, opened_external
    mood: str = "neutral"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

@dataclass
class UserPreferencesRecord:
    user_id: str = "default_user"
    genre_weights: Dict[str, float] = field(default_factory=dict)
    artist_weights: Dict[str, float] = field(default_factory=dict)
    valence_pref: float = 0.0
    energy_pref: float = 0.5
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))