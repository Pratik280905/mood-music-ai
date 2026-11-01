"""
Unit tests for the Multimodal Mood Engine.
"""

import unittest
import numpy as np
from mood_engine.text_emotion import analyze_text_emotion
from mood_engine.face_emotion import analyze_face_emotion
from mood_engine.fusion import fuse_multimodal_emotions
from mood_engine.intensity import calculate_emotional_representation
from mood_engine.trajectory import plan_emotional_journey

class TestMoodEngine(unittest.TestCase):

    def test_text_emotion_joy(self):
        result = analyze_text_emotion("I am so thrilled and happy today, everything went wonderfully!")
        self.assertTrue(result["success"])
        self.assertEqual(result["primary_emotion"], "joy")
        self.assertGreater(result["confidence"], 0.70)
        self.assertIn("joy", result["distribution"])

    def test_text_emotion_sadness(self):
        result = analyze_text_emotion("I feel completely devastated, exhausted, and lonely.")
        self.assertTrue(result["success"])
        self.assertEqual(result["primary_emotion"], "sadness")
        self.assertGreater(result["confidence"], 0.60)

    def test_text_emotion_empty_string(self):
        result = analyze_text_emotion("")
        self.assertTrue(result["success"])
        self.assertEqual(result["primary_emotion"], "neutral")
        self.assertEqual(result["raw_text"], "")

    def test_face_emotion_null_frame(self):
        result = analyze_face_emotion(None)
        self.assertFalse(result["detected"])
        self.assertEqual(result["primary_emotion"], "neutral")
        self.assertIn("error", result)

    def test_face_emotion_black_frame(self):
        black_frame = np.zeros((300, 300, 3), dtype=np.uint8)
        result = analyze_face_emotion(black_frame)
        self.assertFalse(result["detected"])
        self.assertEqual(result["primary_emotion"], "neutral")

    def test_multimodal_fusion_text_only(self):
        text_res = analyze_text_emotion("I am ecstatic and celebrating!")
        face_res = analyze_face_emotion(None)
        fused = fuse_multimodal_emotions(text_res, face_res)
        self.assertEqual(fused["mode"], "text_only")
        self.assertEqual(fused["fused_emotion"], "joy")
        self.assertGreater(fused["confidence"], 0.0)

    def test_multimodal_fusion_baseline(self):
        text_res = analyze_text_emotion("")
        face_res = analyze_face_emotion(None)
        fused = fuse_multimodal_emotions(text_res, face_res)
        self.assertEqual(fused["mode"], "baseline")
        self.assertIn(fused["fused_emotion"], ["neutral", "chill"])

    def test_intensity_and_circumplex_coordinates(self):
        text_res = analyze_text_emotion("I am absolutely bursting with joy and excitement!")
        face_res = analyze_face_emotion(None)
        fused = fuse_multimodal_emotions(text_res, face_res)
        repr_obj = calculate_emotional_representation(fused)

        self.assertIn("valence", repr_obj)
        self.assertIn("energy", repr_obj)
        self.assertIn("intensity", repr_obj)
        self.assertGreater(repr_obj["valence"], 0.0)  # Joy has positive valence
        self.assertGreater(repr_obj["energy"], 0.50)   # Joy has high energy
        self.assertGreater(repr_obj["intensity"], 0.40)

    def test_emotional_trajectory_improve_mood(self):
        journey = plan_emotional_journey("sadness", "Improve My Mood")
        self.assertEqual(journey["strategy"], "Improve My Mood")
        self.assertEqual(journey["starting_emotion"], "sadness")
        self.assertGreater(journey["target_valence"], 0.5)
        self.assertGreater(len(journey["steps"]), 1)
        for s in journey["steps"]:
            self.assertIn("description", s)
            self.assertIn("stage", s)

    def test_emotional_trajectory_match_mood(self):
        journey = plan_emotional_journey("joy", "Match My Mood")
        self.assertEqual(journey["strategy"], "Match My Mood")
        self.assertEqual(len(journey["steps"]), 1)
        for s in journey["steps"]:
            self.assertIn("description", s)
            self.assertIn("stage", s)

    def test_emotional_trajectory_all_strategies(self):
        strategies = ["Match My Mood", "Improve My Mood", "Calm Me Down", "Energize Me"]
        emotions = ["sadness", "anger", "joy", "neutral"]
        for strat in strategies:
            for emo in emotions:
                journey = plan_emotional_journey(emo, strat)
                self.assertIn("steps", journey)
                for s in journey["steps"]:
                    self.assertIn("description", s, f"Missing description in strategy {strat} for emotion {emo}")
                    self.assertIn("stage", s)

if __name__ == "__main__":
    unittest.main()