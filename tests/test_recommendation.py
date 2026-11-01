"""
Unit tests for the Recommendation Engine, Ranking, Personalization, and Explainability.
"""

import unittest
import uuid
from recommendation.ranking import calculate_multi_factor_score, enforce_diversity
from recommendation.fallback_engine import fallback_engine
from recommendation.personalization import PersonalizationEngine
from recommendation.explanation import generate_recommendation_explanation

class TestRecommendationEngine(unittest.TestCase):

    def test_multi_factor_scoring(self):
        score = calculate_multi_factor_score(
            mood_match=0.9,
            desired_mood_match=0.8,
            context_match=0.7,
            user_pref=0.85,
            diversity_bonus=0.8,
            novelty=0.75
        )
        self.assertGreaterEqual(score, 0.05)
        self.assertLessEqual(score, 1.0)
        self.assertGreater(score, 0.70)

    def test_diversity_enforcement(self):
        candidates = [
            {"id": "1", "artist": "Dua Lipa", "genre": "Pop", "score": 0.95},
            {"id": "2", "artist": "Dua Lipa", "genre": "Pop", "score": 0.92},
            {"id": "3", "artist": "Dua Lipa", "genre": "Pop", "score": 0.90},
            {"id": "4", "artist": "Imagine Dragons", "genre": "Rock", "score": 0.88},
            {"id": "5", "artist": "Taylor Swift", "genre": "Pop", "score": 0.85},
            {"id": "6", "artist": "Coldplay", "genre": "Rock", "score": 0.82},
        ]
        diverse = enforce_diversity(candidates, max_per_artist=2, limit=5)
        self.assertEqual(len(diverse), 5)
        dua_count = sum(1 for c in diverse if c["artist"] == "Dua Lipa")
        self.assertLessEqual(dua_count, 2)

    def test_fallback_engine_retrieval(self):
        candidates = fallback_engine.get_candidates(
            current_valence=0.85,
            current_energy=0.80,
            target_valence=0.85,
            target_energy=0.80,
            primary_emotion="joy",
            activity="Party",
            genre_filter="Pop"
        )
        self.assertGreater(len(candidates), 0)
        for c in candidates:
            self.assertEqual(c["genre"], "Pop")
            self.assertIn("mood_match", c)
            self.assertIn("context_match", c)

    def test_personalization_learning(self):
        unique_user = f"user_{uuid.uuid4().hex[:8]}"
        fresh_engine = PersonalizationEngine(user_id=unique_user)
        test_song = {
            "id": f"song_{uuid.uuid4().hex[:6]}",
            "title": "Fresh Beat",
            "artist": "New Indie Artist",
            "genre": "Indie",
            "valence": 0.6,
            "energy": 0.4
        }
        init_score = fresh_engine.calculate_preference_score(test_song)
        self.assertAlmostEqual(init_score, 0.50, delta=0.15)
        # Simulate user liking the song
        fresh_engine.process_feedback(test_song, "liked", mood="joy")
        post_like_score = fresh_engine.calculate_preference_score(test_song)
        self.assertGreater(post_like_score, init_score)

    def test_explanation_generation(self):
        song = {"title": "Levitating", "artist": "Dua Lipa", "genre": "Pop", "valence": 0.88, "energy": 0.84, "activities": ["Party", "Workout"]}
        emotion_repr = {"primary_emotion": "joy", "valence": 0.85, "energy": 0.80}

        exp = generate_recommendation_explanation(
            song=song,
            emotion_repr=emotion_repr,
            strategy="Energize Me",
            activity="Party",
            overall_score=0.92,
            mood_match=0.95,
            context_match=0.90,
            preference_match=0.88,
            novelty=0.75
        )
        self.assertEqual(exp["overall_score_pct"], 92)
        self.assertEqual(exp["mood_match_pct"], 95)
        self.assertGreater(len(exp["reasons"]), 0)

if __name__ == "__main__":
    unittest.main()