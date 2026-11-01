"""
Emotion Intensity Estimation and Normalized Psychological Representation using Russell's Circumplex Model.
"""

from typing import Dict, Any, Optional
import math
from config.settings import EMOTION_COORDINATES
from mood_engine.taxonomy import get_emotion_profile
from utils.validators import clamp

def calculate_emotional_representation(
    fusion_result: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes continuous Valence, Energy, Arousal, and Intensity from the fused probability distribution.

    Produces standard normalized schema:
    {
        "primary_emotion": "joy",
        "confidence": 0.91,
        "intensity": 0.78,
        "valence": 0.72,
        "energy": 0.81,
        "arousal": 0.77,
        "distribution": {...},
        "profile": {...}
    }
    """
    distribution = fusion_result.get("distribution", {})
    primary_emotion = fusion_result.get("fused_emotion", "neutral")
    confidence = fusion_result.get("confidence", 0.5)

    # Calculate weighted expectation of continuous dimensions
    valence_exp = 0.0
    energy_exp = 0.0
    arousal_exp = 0.0

    for emo, prob in distribution.items():
        coords = EMOTION_COORDINATES.get(emo, EMOTION_COORDINATES["neutral"])
        valence_exp += prob * coords["valence"]
        energy_exp += prob * coords["energy"]
        arousal_exp += prob * coords.get("arousal", coords["energy"])

    # Calculate Intensity: Magnitude of emotional deviation from neutral baseline (V=0, E=0.45)
    # scaled by detection confidence
    baseline_dist = math.sqrt((valence_exp ** 2) + ((energy_exp - 0.45) ** 2))
    max_dist = math.sqrt((1.0 ** 2) + (0.55 ** 2))  # max possible deviation
    norm_dist = min(1.0, baseline_dist / max_dist)

    raw_intensity = (0.50 * confidence) + (0.50 * norm_dist)
    intensity = clamp(raw_intensity, 0.15, 1.0)

    profile = get_emotion_profile(primary_emotion)

    return {
        "primary_emotion": primary_emotion,
        "confidence": round(clamp(confidence, 0.0, 1.0), 3),
        "intensity": round(intensity, 3),
        "valence": round(clamp(valence_exp, -1.0, 1.0), 3),
        "energy": round(clamp(energy_exp, 0.0, 1.0), 3),
        "arousal": round(clamp(arousal_exp, 0.0, 1.0), 3),
        "distribution": distribution,
        "mode": fusion_result.get("mode", "baseline"),
        "reasoning": fusion_result.get("reasoning", ""),
        "profile": profile
    }