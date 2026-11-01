"""
Master Recommendation Orchestrator.
Unifies Multimodal Emotion, Emotional Trajectory, Context, Personalization,
Multi-Factor Ranking, Diversity Enforcement, and Explainability.
"""

from typing import Dict, Any, List, Optional
import json
from config.settings import DEFAULT_REC_WEIGHTS
from mood_engine.trajectory import plan_emotional_journey
from recommendation.fallback_engine import fallback_engine
from recommendation.spotify_engine import spotify_engine
from recommendation.personalization import personalization_engine
from recommendation.ranking import calculate_multi_factor_score, enforce_diversity
from recommendation.explanation import generate_recommendation_explanation
from database.repository import MoodRepository
from database.models import MoodSessionRecord
from utils.logging_config import logger

class RecommendationEngine:
    """Coordinates the entire end-to-end music recommendation pipeline."""

    def __init__(self):
        self.fallback = fallback_engine
        self.spotify = spotify_engine
        self.personalization = personalization_engine

    def generate_recommendations(
        self,
        emotion_repr: Dict[str, Any],
        context: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None,
        user_id: str = "default_user",
        limit: int = 6
    ) -> Dict[str, Any]:
        """
        Executes full multi-stage recommendation workflow.
        """
        primary_emotion = emotion_repr.get("primary_emotion", "neutral")
        curr_val = emotion_repr.get("valence", 0.0)
        curr_eng = emotion_repr.get("energy", 0.5)

        activity = context.get("activity", "Study")
        strategy = context.get("strategy", "Match My Mood")
        genre_filter = context.get("genre", "All")
        language_filter = context.get("language", "All")

        # 1. Plan Emotional Journey / Trajectory
        journey = plan_emotional_journey(current_emotion=primary_emotion, strategy=strategy)
        target_val = journey["target_valence"]
        target_eng = journey["target_energy"]

        active_source = "local_fallback"
        source_note = "Operating in Local AI Recommendation Engine mode (zero API dependency)."

        # 2. Attempt Spotify Discovery if enabled
        candidates: List[Dict[str, Any]] = []
        spot_res = self.spotify.get_candidates(
            primary_emotion=primary_emotion,
            activity=activity,
            genre_filter=genre_filter,
            limit=limit * 3
        )

        if spot_res.get("source") == "spotify" and spot_res.get("tracks"):
            active_source = "spotify"
            source_note = "Spotify Web API connected: Displaying catalog search results."
            for t in spot_res["tracks"]:
                candidates.append({
                    "id": t["id"],
                    "title": t["title"],
                    "artist": t["artist"],
                    "genre": genre_filter if genre_filter != "All" else "Spotify Track",
                    "language": "English",
                    "valence": target_val,
                    "energy": target_eng,
                    "activities": [activity],
                    "spotify_url": t["spotify_url"],
                    "source": "spotify",
                    "mood_match": 0.88,
                    "desired_mood_match": 0.85,
                    "context_match": 0.80
                })

        # If Spotify not connected or yielded no tracks, use rich local catalog
        if not candidates:
            active_source = "local_fallback"
            if spot_res.get("error"):
                source_note = f"Spotify API unavailable ({spot_res['error']}). Switched smoothly to Local AI Catalog."
            candidates = self.fallback.get_candidates(
                current_valence=curr_val,
                current_energy=curr_eng,
                target_valence=target_val,
                target_energy=target_eng,
                primary_emotion=primary_emotion,
                activity=activity,
                genre_filter=genre_filter,
                language_filter=language_filter
            )

        # 3. Score and Rank Candidates with Personalization & Diversity
        scored_candidates: List[Dict[str, Any]] = []
        for song in candidates:
            pref_score = self.personalization.calculate_preference_score(song)
            nov_score = self.personalization.calculate_novelty_score(song)
            div_bonus = 0.80

            final_score = calculate_multi_factor_score(
                mood_match=song.get("mood_match", 0.5),
                desired_mood_match=song.get("desired_mood_match", 0.5),
                context_match=song.get("context_match", 0.5),
                user_pref=pref_score,
                diversity_bonus=div_bonus,
                novelty=nov_score,
                weights=weights
            )

            # Generate Explainable AI breakdown
            explanation = generate_recommendation_explanation(
                song=song,
                emotion_repr=emotion_repr,
                strategy=strategy,
                activity=activity,
                overall_score=final_score,
                mood_match=song.get("mood_match", 0.5),
                context_match=song.get("context_match", 0.5),
                preference_match=pref_score,
                novelty=nov_score
            )

            scored_candidates.append({
                **song,
                "score": final_score,
                "preference_score": pref_score,
                "novelty_score": nov_score,
                "explanation": explanation
            })

        # 4. Enforce Diversity (Max 2 songs per artist)
        final_playlist = enforce_diversity(scored_candidates, max_per_artist=2, limit=limit)

        # 5. Persist Session & Recommendations to SQLite
        try:
            session_rec = MoodSessionRecord(
                text_input=context.get("raw_text", ""),
                has_face=context.get("has_face", False),
                text_emotion=emotion_repr.get("text_primary", primary_emotion),
                face_emotion=emotion_repr.get("face_primary", primary_emotion),
                fused_emotion=primary_emotion,
                intensity=emotion_repr.get("intensity", 0.5),
                valence=curr_val,
                energy=curr_eng,
                strategy=strategy,
                activity=activity,
                context_json=json.dumps(context)
            )
            session_id = MoodRepository.create_mood_session(session_rec)
            MoodRepository.save_recommendations(session_id, final_playlist)
        except Exception as e:
            logger.error(f"Failed to record session in database: {e}")
            session_id = None

        logger.info(f"Generated {len(final_playlist)} recommendations using {active_source}.")

        return {
            "session_id": session_id,
            "active_source": active_source,
            "source_note": source_note,
            "journey": journey,
            "recommendations": final_playlist
        }

recommendation_engine = RecommendationEngine()