"""
Explainable AI (XAI) Engine for Music Recommendations.
Generates multi-attribute metric breakdowns and human-interpretable rationale bullets.
"""

from typing import Dict, Any, List

def generate_recommendation_explanation(
    song: Dict[str, Any],
    emotion_repr: Dict[str, Any],
    strategy: str,
    activity: str,
    overall_score: float,
    mood_match: float,
    context_match: float,
    preference_match: float,
    novelty: float
) -> Dict[str, Any]:
    """
    Constructs an explainability packet for a single recommended track.
    """
    primary_emotion = emotion_repr.get("primary_emotion", "neutral")
    user_valence = emotion_repr.get("valence", 0.0)
    user_energy = emotion_repr.get("energy", 0.5)

    song_genre = song.get("genre", "Music")
    song_artist = song.get("artist", "Artist")
    song_energy = float(song.get("energy", 0.5))
    song_valence = float(song.get("valence", 0.0))

    reasons: List[str] = []

    # 1. Emotional Alignment Rationale
    if mood_match >= 0.80:
        reasons.append(f"Strong emotional congruence with your detected {primary_emotion.upper()} state ({mood_match:.0%}).")
    elif mood_match >= 0.60:
        reasons.append(f"Harmonizes with your {primary_emotion.upper()} emotional frequency.")
    else:
        reasons.append("Provides a complementary emotional counterpoint.")

    # 2. Strategy / Journey Rationale
    if strategy == "Improve My Mood":
        reasons.append(f"Features uplifting harmonic brightness (valence: {song_valence:+.2f}) to elevate your mood.")
    elif strategy == "Calm Me Down":
        reasons.append(f"Gentle rhythmic pacing and reduced arousal (energy: {song_energy:.2f}) to induce tranquility.")
    elif strategy == "Energize Me":
        reasons.append(f"High-octane tempo and kinetic dynamics (energy: {song_energy:.2f}) to ignite physical energy.")
    else:
        reasons.append("Tonal characteristics mirror your present emotional state for deep resonance.")

    # 3. Context & Activity Rationale
    if activity in song.get("activities", []):
        reasons.append(f"Acoustically optimized for '{activity}' with suitable focus and dynamic depth.")
    else:
        reasons.append(f"Selected genre ({song_genre}) complements your '{activity}' session.")

    # 4. Personalization & Taste Rationale
    if preference_match >= 0.70:
        reasons.append(f"Directly reflects your affinity for {song_genre} and tracks by {song_artist}.")
    elif novelty >= 0.85:
        reasons.append("Fresh discovery: Curated to introduce diverse musical perspectives into your rotation.")

    return {
        "overall_score_pct": int(overall_score * 100),
        "mood_match_pct": int(mood_match * 100),
        "context_match_pct": int(context_match * 100),
        "preference_match_pct": int(preference_match * 100),
        "novelty_pct": int(novelty * 100),
        "reasons": reasons[:4],
        "summary": f"{song.get('title')} was selected with {int(overall_score * 100)}% confidence."
    }