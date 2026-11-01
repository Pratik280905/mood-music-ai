"""
Multi-factor recommendation ranking and diversity-aware candidate selection.
"""

from typing import List, Dict, Any, Optional
from config.settings import DEFAULT_REC_WEIGHTS
from utils.validators import clamp

def calculate_multi_factor_score(
    mood_match: float,
    desired_mood_match: float,
    context_match: float,
    user_pref: float,
    diversity_bonus: float,
    novelty: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Computes a weighted composite score in [0.0, 1.0].

    Equation:
        score = (w_m * mood_match) + (w_g * desired_mood_match) +
                (w_c * context_match) + (w_p * user_pref) +
                (w_d * diversity) + (w_n * novelty)
    """
    w = weights or DEFAULT_REC_WEIGHTS
    total = (
        (w.get("mood_match", 0.30) * mood_match) +
        (w.get("desired_mood_match", 0.20) * desired_mood_match) +
        (w.get("context_match", 0.15) * context_match) +
        (w.get("user_preference", 0.15) * user_pref) +
        (w.get("diversity", 0.10) * diversity_bonus) +
        (w.get("novelty", 0.10) * novelty)
    )
    return round(clamp(total, 0.05, 0.99), 3)

def enforce_diversity(
    candidates: List[Dict[str, Any]],
    max_per_artist: int = 2,
    limit: int = 6
) -> List[Dict[str, Any]]:
    """
    Filters candidates to guarantee artist and genre variety.
    Avoids recommending multiple songs from the same artist consecutively.
    """
    selected: List[Dict[str, Any]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    # Sort primarily by score descending
    sorted_candidates = sorted(candidates, key=lambda c: c.get("score", 0.0), reverse=True)

    for item in sorted_candidates:
        artist = item.get("artist", "").strip()
        genre = item.get("genre", "").strip()

        curr_artist_count = artist_counts.get(artist, 0)
        if curr_artist_count >= max_per_artist:
            continue

        selected.append(item)
        artist_counts[artist] = curr_artist_count + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

        if len(selected) >= limit:
            break

    # If strict diversity couldn't fill the quota, backfill from remaining
    if len(selected) < limit:
        for item in sorted_candidates:
            if item not in selected:
                selected.append(item)
                if len(selected) >= limit:
                    break

    return selected