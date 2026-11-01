"""
Transformer-based NLP Emotion Classification using Hugging Face DistilRoBERTa.
"""

from functools import lru_cache
from typing import Dict, Any, Tuple
from transformers import pipeline
from config.settings import HF_EMOTION_MODEL, EMOTIONS
from mood_engine.taxonomy import normalize_emotion_label
from utils.logging_config import logger

@lru_cache(maxsize=1)
def _get_emotion_pipeline():
    """Loads and caches the Hugging Face transformer pipeline in memory."""
    logger.info(f"Loading NLP Emotion Transformer model: {HF_EMOTION_MODEL}")
    try:
        return pipeline(
            "text-classification",
            model=HF_EMOTION_MODEL,
            top_k=None,
            truncation=True,
            max_length=512
        )
    except Exception as e:
        logger.error(f"Failed to load transformer model '{HF_EMOTION_MODEL}': {e}")
        return None

def analyze_text_emotion(text: str) -> Dict[str, Any]:
    """
    Analyzes free-form user text and returns emotion distribution and confidence.

    Returns:
        {
            "success": bool,
            "primary_emotion": str,
            "confidence": float,
            "distribution": dict[str, float],
            "raw_text": str,
            "error": str | None
        }
    """
    cleaned = (text or "").strip()
    if not cleaned:
        # Neutral baseline when no text is provided
        default_dist = {e: (0.5 if e in ["neutral", "chill"] else 0.05) for e in EMOTIONS}
        total = sum(default_dist.values())
        norm_dist = {k: round(v / total, 4) for k, v in default_dist.items()}
        return {
            "success": True,
            "primary_emotion": "neutral",
            "confidence": 0.50,
            "distribution": norm_dist,
            "raw_text": "",
            "error": "No text provided (defaulted to neutral equilibrium)."
        }

    classifier = _get_emotion_pipeline()
    if classifier is None:
        # Safe fallback if pipeline fails to initialize
        logger.warning("Pipeline unavailable. Utilizing fallback text classifier.")
        return _fallback_text_classifier(cleaned)

    try:
        results = classifier(cleaned)[0]  # list of {"label": str, "score": float}
        raw_dist: Dict[str, float] = {}

        for item in results:
            raw_label = item["label"].lower()
            canonical = normalize_emotion_label(raw_label)
            score = float(item["score"])
            raw_dist[canonical] = raw_dist.get(canonical, 0.0) + score

        # Ensure all canonical emotions are present in distribution
        for emo in EMOTIONS:
            raw_dist.setdefault(emo, 0.001)

        # Normalize to sum to 1.0
        total_score = sum(raw_dist.values())
        normalized_dist = {emo: round(score / total_score, 4) for emo, score in raw_dist.items()}

        # Identify top emotion
        primary_emotion = max(normalized_dist.items(), key=lambda x: x[1])[0]
        confidence = normalized_dist[primary_emotion]

        logger.info(f"Text emotion detected: '{primary_emotion}' (confidence: {confidence:.2%})")

        return {
            "success": True,
            "primary_emotion": primary_emotion,
            "confidence": round(confidence, 4),
            "distribution": normalized_dist,
            "raw_text": cleaned,
            "error": None
        }

    except Exception as e:
        logger.error(f"Error during transformer text emotion inference: {e}")
        return _fallback_text_classifier(cleaned, error=str(e))

def _fallback_text_classifier(text: str, error: str = None) -> Dict[str, Any]:
    """Lightweight rule-based fallback if neural transformer encounters an error."""
    text_lower = text.lower()
    scores = {e: 0.05 for e in EMOTIONS}

    keywords = {
        "joy": ["happy", "great", "awesome", "excited", "love", "joy", "fantastic", "good", "wonderful", "celebrate"],
        "sadness": ["sad", "depressed", "down", "cry", "lonely", "exhausted", "tired", "heartbroken", "gloomy", "unhappy"],
        "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "hate", "irritated", "pissed"],
        "fear": ["scared", "afraid", "anxious", "nervous", "worried", "panic", "stressed"],
        "surprise": ["surprised", "shocked", "amazed", "unbelievable", "wow", "unexpected"],
        "disgust": ["disgusted", "gross", "sick", "nasty", "revolting"],
        "chill": ["chill", "relaxed", "peaceful", "calm", "mellow", "serene", "quiet"],
        "neutral": ["okay", "fine", "normal", "average", "regular"]
    }

    for emo, words in keywords.items():
        for w in words:
            if w in text_lower:
                scores[emo] += 0.35

    total = sum(scores.values())
    norm_dist = {k: round(v / total, 4) for k, v in scores.items()}
    primary = max(norm_dist.items(), key=lambda x: x[1])[0]

    return {
        "success": True,
        "primary_emotion": primary,
        "confidence": norm_dist[primary],
        "distribution": norm_dist,
        "raw_text": text,
        "error": error or "Transformer unavailable; rule-based fallback applied."
    }