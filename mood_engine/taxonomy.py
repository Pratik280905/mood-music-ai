"""
Emotion taxonomy, mappings, and circumplex space coordinates.
"""

import math
from config.settings import EMOTIONS, EMOTION_COORDINATES, EMOTION_PROFILES

RAW_LABEL_MAPPING = {
    "joy": "joy",
    "happiness": "joy",
    "happy": "joy",
    "love": "joy",
    "optimism": "joy",
    "surprise": "surprise",
    "excited": "surprise",
    "neutral": "neutral",
    "calm": "chill",
    "chill": "chill",
    "relaxed": "chill",
    "peaceful": "chill",
    "sadness": "sadness",
    "sad": "sadness",
    "grief": "sadness",
    "depressed": "sadness",
    "fear": "fear",
    "anxious": "fear",
    "nervous": "fear",
    "anger": "anger",
    "angry": "anger",
    "annoyed": "anger",
    "rage": "anger",
    "disgust": "disgust",
    "aversion": "disgust",
}

def normalize_emotion_label(raw_label: str) -> str:
    """Maps arbitrary emotion text to the canonical taxonomy."""
    if not raw_label:
        return "neutral"
    clean = raw_label.strip().lower()
    return RAW_LABEL_MAPPING.get(clean, "neutral")

def get_emotion_profile(emotion: str) -> dict:
    """Retrieves display profile (emoji, label, color, description) for an emotion."""
    normalized = normalize_emotion_label(emotion)
    return EMOTION_PROFILES.get(normalized, EMOTION_PROFILES["neutral"])

def get_emotion_coords(emotion: str) -> dict:
    """Returns Russell Circumplex coordinates (valence, energy, arousal)."""
    normalized = normalize_emotion_label(emotion)
    return EMOTION_COORDINATES.get(normalized, EMOTION_COORDINATES["neutral"])

def emotion_distance(coords1: dict, coords2: dict) -> float:
    """Calculates Euclidean distance in normalized (valence, energy) 2D space."""
    v1, e1 = coords1.get("valence", 0.0), coords1.get("energy", 0.5)
    v2, e2 = coords2.get("valence", 0.0), coords2.get("energy", 0.5)
    # Map valence [-1, 1] to [0, 1] for balanced euclidean distance
    nv1 = (v1 + 1.0) / 2.0
    nv2 = (v2 + 1.0) / 2.0
    return math.sqrt((nv1 - nv2) ** 2 + (e1 - e2) ** 2)