"""
Unit tests for the SQLite Database and Repository layer.
"""

import unittest
from database.models import MoodSessionRecord
from database.repository import MoodRepository

class TestDatabaseRepository(unittest.TestCase):

    def test_create_session_and_retrieve(self):
        rec = MoodSessionRecord(
            text_input="Testing SQLite repository session recording",
            has_face=False,
            text_emotion="joy",
            face_emotion="neutral",
            fused_emotion="joy",
            intensity=0.85,
            valence=0.8,
            energy=0.75,
            strategy="Match My Mood",
            activity="Workout"
        )
        session_id = MoodRepository.create_mood_session(rec)
        self.assertIsNotNone(session_id)
        self.assertGreater(session_id, 0)

        history = MoodRepository.get_mood_sessions(limit=5)
        self.assertGreater(len(history), 0)
        latest = history[0]
        self.assertEqual(latest["fused_emotion"], "joy")

    def test_record_feedback_and_summary(self):
        MoodRepository.record_feedback(
            song_id="s_test_1",
            song_title="Good Life",
            artist="OneRepublic",
            genre="Pop",
            action="liked",
            mood="joy"
        )
        summary = MoodRepository.get_feedback_summary()
        self.assertIn("action_counts", summary)
        self.assertGreaterEqual(summary["likes"], 1)

        liked = MoodRepository.get_liked_songs()
        self.assertTrue(any(s["song_id"] == "s_test_1" for s in liked))

if __name__ == "__main__":
    unittest.main()