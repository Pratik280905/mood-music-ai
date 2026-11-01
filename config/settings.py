"""
Application settings and configurations for MoodMuse AI.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

DB_PATH = DATABASE_DIR / "moodmuse.db"
SONGS_CSV_PATH = DATA_DIR / "songs.csv"
LOG_FILE_PATH = LOG_DIR / "moodmuse.log"

# Create directories if they do not exist
for directory in [DATA_DIR, DATABASE_DIR, LOG_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback").strip()

# App Version & Identity
APP_NAME = "MoodMuse AI"
APP_TAGLINE = "Multimodal Personalized Music Intelligence"
APP_VERSION = "2.0.0"

# Canonical Emotion Taxonomy
EMOTIONS = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "chill", "neutral"]

# Russell Circumplex Model Coordinates (Valence: [-1.0, 1.0], Energy/Arousal: [0.0, 1.0])
EMOTION_COORDINATES = {
    "joy": {"valence": 0.85, "energy": 0.80, "arousal": 0.78},
    "surprise": {"valence": 0.60, "energy": 0.85, "arousal": 0.85},
    "chill": {"valence": 0.65, "energy": 0.40, "arousal": 0.35},
    "neutral": {"valence": 0.05, "energy": 0.45, "arousal": 0.40},
    "sadness": {"valence": -0.75, "energy": 0.25, "arousal": 0.25},
    "fear": {"valence": -0.65, "energy": 0.70, "arousal": 0.75},
    "anger": {"valence": -0.80, "energy": 0.85, "arousal": 0.88},
    "disgust": {"valence": -0.70, "energy": 0.55, "arousal": 0.60},
}

# Emotion Presentation Profiles (Emoji, Label, Color Palette, Description)
EMOTION_PROFILES = {
    "joy": {
        "emoji": "😄",
        "label": "Joyful / Euphoric",
        "color": "#FFB300",
        "accent": "#FFA000",
        "gradient": "linear-gradient(135deg, #1f1d14 0%, #3e3205 100%)",
        "description": "High positive sentiment, vibrant energy, and cheerful affect."
    },
    "surprise": {
        "emoji": "😲",
        "label": "Surprised / Excited",
        "color": "#FF7043",
        "accent": "#F4511E",
        "gradient": "linear-gradient(135deg, #241613 0%, #4a2118 100%)",
        "description": "Heightened arousal, sudden awareness, and receptive cognitive state."
    },
    "chill": {
        "emoji": "😌",
        "label": "Chill / Serene",
        "color": "#26A69A",
        "accent": "#00897B",
        "gradient": "linear-gradient(135deg, #11201d 0%, #153c37 100%)",
        "description": "Gentle positive valence with low arousal; balanced and relaxed."
    },
    "neutral": {
        "emoji": "😐",
        "label": "Neutral / Balanced",
        "color": "#78909C",
        "accent": "#546E7A",
        "gradient": "linear-gradient(135deg, #161a1d 0%, #263238 100%)",
        "description": "Equilibrium state with moderate energy and mild valence."
    },
    "sadness": {
        "emoji": "😢",
        "label": "Melancholic / Sad",
        "color": "#42A5F5",
        "accent": "#1E88E5",
        "gradient": "linear-gradient(135deg, #101c28 0%, #173753 100%)",
        "description": "Subdued energy, introspective and reflective emotional state."
    },
    "fear": {
        "emoji": "😨",
        "label": "Anxious / Apprehensive",
        "color": "#AB47BC",
        "accent": "#8E24AA",
        "gradient": "linear-gradient(135deg, #1e1324 0%, #3a1c47 100%)",
        "description": "Elevated alertness, tense arousal, and cautious emotional response."
    },
    "anger": {
        "emoji": "😠",
        "label": "Agitated / Angry",
        "color": "#EF5350",
        "accent": "#E53935",
        "gradient": "linear-gradient(135deg, #281212 0%, #4f1b1b 100%)",
        "description": "High kinetic energy, sharp focus, intense emotional tension."
    },
    "disgust": {
        "emoji": "😒",
        "label": "Averse / Frustrated",
        "color": "#8D6E63",
        "accent": "#6D4C41",
        "gradient": "linear-gradient(135deg, #201815 0%, #3d2c26 100%)",
        "description": "Resistant cognitive sentiment with moderate agitation."
    },
}

# Context Activities and Profiles
ACTIVITIES = {
    "Study": {
        "energy_range": (0.2, 0.55),
        "target_valence": (0.4, 0.8),
        "favored_genres": ["Lo-Fi", "Classical", "Ambient", "Acoustic"],
        "description": "Unobtrusive melodies and focus-enhancing tempos."
    },
    "Workout": {
        "energy_range": (0.75, 1.0),
        "target_valence": (0.5, 0.95),
        "favored_genres": ["Rock", "Electronic", "Hip-Hop", "Pop", "Metal"],
        "description": "Driving rhythms, energetic beats, and motivating dynamics."
    },
    "Relax": {
        "energy_range": (0.1, 0.45),
        "target_valence": (0.5, 0.9),
        "favored_genres": ["Ambient", "Acoustic", "Lo-Fi", "Jazz"],
        "description": "Gentle harmonies, acoustic textures, and soothing pacing."
    },
    "Travel": {
        "energy_range": (0.4, 0.75),
        "target_valence": (0.5, 0.9),
        "favored_genres": ["Indie", "Pop", "Rock", "Hip-Hop"],
        "description": "Scenic pacing with dynamic rhythm and melodic storytelling."
    },
    "Sleep": {
        "energy_range": (0.0, 0.25),
        "target_valence": (0.3, 0.7),
        "favored_genres": ["Ambient", "Classical", "Acoustic"],
        "description": "Minimal percussion, slow tempos, and peaceful soundscapes."
    },
    "Party": {
        "energy_range": (0.8, 1.0),
        "target_valence": (0.7, 1.0),
        "favored_genres": ["Pop", "Electronic", "Hip-Hop", "Dance"],
        "description": "High-octane basslines, danceable grooves, and uplifting hooks."
    },
    "Focus": {
        "energy_range": (0.3, 0.6),
        "target_valence": (0.4, 0.8),
        "favored_genres": ["Lo-Fi", "Electronic", "Classical", "Ambient"],
        "description": "Steady beats with low cognitive load to sustain flow state."
    },
    "Coding": {
        "energy_range": (0.35, 0.7),
        "target_valence": (0.4, 0.85),
        "favored_genres": ["Electronic", "Lo-Fi", "Ambient", "Synthwave", "Rock"],
        "description": "Rhythmic pulse, synth textures, and deep immersion."
    },
    "Commute": {
        "energy_range": (0.45, 0.75),
        "target_valence": (0.4, 0.85),
        "favored_genres": ["Indie", "Pop", "Hip-Hop", "Rock"],
        "description": "Engaging hooks to brighten daily transit."
    },
}

# Recommendation Strategies (Emotional Journey)
STRATEGIES = {
    "Match My Mood": {
        "label": "Match My Mood",
        "description": "Matches current emotional resonance for validation and catharsis."
    },
    "Improve My Mood": {
        "label": "Improve My Mood",
        "description": "Constructs a gradual uplifting path toward positive valence and optimism."
    },
    "Calm Me Down": {
        "label": "Calm Me Down",
        "description": "De-escalates tension and guides emotional state toward tranquility and peace."
    },
    "Energize Me": {
        "label": "Energize Me",
        "description": "Ignites motivation and boosts energetic arousal."
    },
}

# Default Multi-Factor Recommendation Weights
DEFAULT_REC_WEIGHTS = {
    "mood_match": 0.30,
    "desired_mood_match": 0.20,
    "context_match": 0.15,
    "user_preference": 0.15,
    "diversity": 0.10,
    "novelty": 0.10,
}

# Default Multimodal Fusion Weights
DEFAULT_FUSION_WEIGHTS = {
    "text_weight": 0.60,
    "face_weight": 0.40,
}

# NLP Transformer Model
HF_EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
HF_VISION_EMOTION_MODEL = "dima806/facial_emotions_image_detection"

# Ethical AI Disclaimer
ETHICAL_DISCLAIMER = (
    "AI Transparency Notice: Emotion detection is an algorithmic estimation based on multimodal "
    "signals (text semantics and facial geometry). It is designed purely for music curation and "
    "must not be interpreted as a psychological, clinical, or medical assessment."
)