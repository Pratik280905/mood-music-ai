"""
Emotional Journey & Mood Trajectory Planner.
Implements the Iso-Principle of music therapy: meets the listener where they are
and gradually transforms their emotional state toward the desired goal.
"""

from typing import Dict, Any, List
from config.settings import EMOTION_COORDINATES
from mood_engine.taxonomy import normalize_emotion_label
from utils.validators import clamp

JOURNEY_TEMPLATES = {
    "Improve My Mood": {
        "from_negative": [
            {"stage": "Catharsis & Reflection", "emotion": "sadness", "valence": -0.45, "energy": 0.35, "description": "Emotionally resonant acoustic harmony for cathartic acknowledgment."},
            {"stage": "Emotional Grounding", "emotion": "neutral", "valence": 0.10, "energy": 0.40, "description": "Balanced pacing and steady tempo to stabilize mood."},
            {"stage": "Hope & Curiosity", "emotion": "chill", "valence": 0.45, "energy": 0.50, "description": "Warm melodies and brightening chord structures."},
            {"stage": "Uplifting Joy", "emotion": "joy", "valence": 0.80, "energy": 0.75, "description": "Vibrant, euphoric rhythms to sustain optimism."}
        ],
        "from_positive": [
            {"stage": "Savoring Joy", "emotion": "joy", "valence": 0.80, "energy": 0.70, "description": "Celebratory rhythms that honor positive sentiment."},
            {"stage": "Inspiration Peak", "emotion": "surprise", "valence": 0.85, "energy": 0.85, "description": "Dynamic crescendos and exhilarating melodies."}
        ]
    },
    "Calm Me Down": {
        "from_agitated": [
            {"stage": "De-escalation", "emotion": "anger", "valence": -0.30, "energy": 0.65, "description": "Channelling raw kinetic tension into structured rhythm."},
            {"stage": "Centering & Breath", "emotion": "neutral", "valence": 0.20, "energy": 0.45, "description": "Mellow percussion and grounding bass textures."},
            {"stage": "Tranquil Stillness", "emotion": "chill", "valence": 0.60, "energy": 0.25, "description": "Soft ambient acoustics and slow tempo for deep relaxation."}
        ],
        "from_calm": [
            {"stage": "Deep Serenity", "emotion": "chill", "valence": 0.70, "energy": 0.20, "description": "Ethereal soundscapes and peaceful lullabies."}
        ]
    },
    "Energize Me": {
        "default": [
            {"stage": "Gentle Awakening", "emotion": "neutral", "valence": 0.25, "energy": 0.45, "description": "Smooth mid-tempo groove to initiate momentum."},
            {"stage": "Rhythmic Acceleration", "emotion": "chill", "valence": 0.55, "energy": 0.65, "description": "Crisp percussion and driving basslines."},
            {"stage": "Peak Motivation", "emotion": "joy", "valence": 0.85, "energy": 0.90, "description": "High-octane synth drops, infectious hooks, and peak bpm."}
        ]
    }
}

def plan_emotional_journey(current_emotion: str, strategy: str = "Match My Mood") -> Dict[str, Any]:
    """
    Plans an emotional transition pathway from current affect to destination affect.
    """
    curr_norm = normalize_emotion_label(current_emotion)
    curr_coords = EMOTION_COORDINATES.get(curr_norm, EMOTION_COORDINATES["neutral"])
    v_start = curr_coords["valence"]
    e_start = curr_coords["energy"]

    if strategy == "Match My Mood":
        steps = [
            {
                "step": 1,
                "stage": "Emotional Resonance",
                "emotion": curr_norm,
                "valence": v_start,
                "energy": e_start,
                "description": f"Validates and mirrors your current {curr_norm.upper()} state through tonal congruency."
            }
        ]
        narrative = f"Musical selection matches your current {curr_norm.upper()} state, providing deep resonance and emotional presence."
        target_v = v_start
        target_e = e_start

    elif strategy == "Improve My Mood":
        if v_start < 0.1:
            template = JOURNEY_TEMPLATES["Improve My Mood"]["from_negative"]
        else:
            template = JOURNEY_TEMPLATES["Improve My Mood"]["from_positive"]

        steps = [{"step": i + 1, **stage} for i, stage in enumerate(template)]
        target_v = steps[-1]["valence"]
        target_e = steps[-1]["energy"]
        narrative = (
            f"Using the Iso-Principle, the playlist starts near your {curr_norm.upper()} state "
            f"and incrementally guides your emotional affect toward hope and uplifting joy."
        )

    elif strategy == "Calm Me Down":
        if e_start > 0.5 or v_start < 0:
            template = JOURNEY_TEMPLATES["Calm Me Down"]["from_agitated"]
        else:
            template = JOURNEY_TEMPLATES["Calm Me Down"]["from_calm"]

        steps = [{"step": i + 1, **stage} for i, stage in enumerate(template)]
        target_v = steps[-1]["valence"]
        target_e = steps[-1]["energy"]
        narrative = "Gradually filters out abrasive high-tempo spikes, replacing tension with serene, grounding soundscapes."

    elif strategy == "Energize Me":
        template = JOURNEY_TEMPLATES["Energize Me"]["default"]
        steps = [{"step": i + 1, **stage} for i, stage in enumerate(template)]
        target_v = steps[-1]["valence"]
        target_e = steps[-1]["energy"]
        narrative = "Progressively increases tempo, rhythm density, and harmonic brightness to elevate physiological arousal."

    else:
        # Fallback to Match
        steps = [{"step": 1, "stage": "Direct Match", "emotion": curr_norm, "valence": v_start, "energy": e_start, "description": "Standard mood matching."}]
        narrative = "Standard mood matching."
        target_v = v_start
        target_e = e_start

    return {
        "strategy": strategy,
        "starting_emotion": curr_norm,
        "target_valence": round(target_v, 2),
        "target_energy": round(target_e, 2),
        "steps": steps,
        "narrative": narrative
    }