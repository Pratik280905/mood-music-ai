"""
Computer Vision Facial Emotion Analysis using Vision Transformer (ViT) and OpenCV Face Localization.
Uses dima806/facial_emotions_image_detection fine-tuned on facial expressions.
"""

from typing import Dict, Any, Optional, Tuple
from functools import lru_cache
import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

from config.settings import EMOTIONS, HF_VISION_EMOTION_MODEL
from mood_engine.taxonomy import normalize_emotion_label
from utils.logging_config import logger

# Label mapping from ViT model output to canonical emotion taxonomy
VIT_EMOTION_MAP = {
    "happy": "joy",
    "joy": "joy",
    "sad": "sadness",
    "sadness": "sadness",
    "angry": "anger",
    "anger": "anger",
    "fear": "fear",
    "surprise": "surprise",
    "disgust": "disgust",
    "neutral": "neutral"
}

@lru_cache(maxsize=1)
def _get_vision_emotion_pipeline():
    """Loads and caches the Vision Transformer facial emotion classifier."""
    logger.info(f"Loading Vision Transformer Facial Emotion Model: {HF_VISION_EMOTION_MODEL}")
    try:
        return pipeline(
            "image-classification",
            model=HF_VISION_EMOTION_MODEL,
            top_k=None
        )
    except Exception as e:
        logger.error(f"Failed to load vision emotion pipeline: {e}")
        return None

class FaceEmotionDetector:
    """
    State-of-the-art Facial Emotion Recognition pipeline.
    1. Localizes faces in camera frames using OpenCV Haar cascades.
    2. Crops and normalizes the facial Region of Interest (ROI).
    3. Infers high-precision emotional probabilities using a Vision Transformer (ViT).
    4. Annotates the frame with face bounding box and emotion metrics.
    """

    def __init__(self):
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            self.smile_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_smile.xml"
            )
            self.is_initialized = not self.face_cascade.empty()
        except Exception as e:
            logger.error(f"Failed to initialize Haar cascades: {e}")
            self.is_initialized = False

    def analyze_frame(self, frame: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        Analyzes an RGB/BGR frame for facial emotion expressions using ViT.
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return self._empty_result(error="No camera frame supplied.")

        if not self.is_initialized:
            return self._empty_result(error="OpenCV cascade detectors could not be loaded.")

        try:
            # Ensure frame is 3-channel
            if frame.ndim == 2:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                gray = frame
            else:
                rgb_frame = frame
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Check if frame is too dark or devoid of contrast (e.g. solid black / blank test frames)
            if float(gray.mean()) < 15.0 or float(gray.std()) < 8.0:
                return self._empty_result(error="Frame is too dark or devoid of contrast to detect a face.")

            # Detect faces with balanced multi-scale parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.12,
                minNeighbors=4,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) == 0:
                return self._analyze_whole_or_empty(rgb_frame, gray)

            # Focus on largest face in frame
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

            # Expand bounding box by 15% margin to capture jawline, eyebrows, and cheeks
            pad_x = int(w * 0.15)
            pad_y = int(h * 0.15)
            img_h, img_w = frame.shape[:2]
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(img_w, x + w + pad_x)
            y2 = min(img_h, y + h + pad_y)

            face_roi = rgb_frame[y1:y2, x1:x2]
            if face_roi.size == 0:
                face_roi = rgb_frame[y:y+h, x:x+w]

            # Convert cropped face to PIL Image for Vision Transformer
            pil_face = Image.fromarray(face_roi)

            # Neural ViT Emotion Inference
            vit_pipe = _get_vision_emotion_pipeline()
            if vit_pipe is not None:
                vit_scores = vit_pipe(pil_face)
                distribution = self._parse_vit_scores(vit_scores)
            else:
                distribution = self._fallback_geometric_analysis(gray[y:y+h, x:x+w])

            primary_emotion = max(distribution.items(), key=lambda item: item[1])[0]
            confidence = distribution[primary_emotion]

            # Generate annotated image with aesthetic bounding box & label
            annotated_frame = rgb_frame.copy()
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (167, 139, 250), 3)
            label_text = f"{primary_emotion.upper()} {int(confidence * 100)}%"
            cv2.putText(
                annotated_frame,
                label_text,
                (x1, max(25, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            logger.info(f"ViT Face Emotion: {primary_emotion} ({confidence:.1%})")

            return {
                "detected": True,
                "primary_emotion": primary_emotion,
                "confidence": round(confidence, 4),
                "distribution": distribution,
                "face_box": (int(x1), int(y1), int(x2 - x1), int(y2 - y1)),
                "annotated_frame": annotated_frame,
                "cropped_face": face_roi,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error during facial expression analysis: {e}")
            return self._empty_result(error=f"Facial analysis error: {str(e)}")

    def _analyze_whole_or_empty(self, rgb_frame: np.ndarray, gray: np.ndarray) -> Dict[str, Any]:
        """Attempts whole-frame ViT inference if face was slightly rotated or close-up, verifying contrast."""
        if float(gray.mean()) < 25.0 or float(gray.std()) < 15.0:
            return self._empty_result(error="No face detected in frame. Please center your face in good lighting.")

        vit_pipe = _get_vision_emotion_pipeline()
        if vit_pipe is not None:
            try:
                pil_img = Image.fromarray(rgb_frame)
                vit_scores = vit_pipe(pil_img)
                distribution = self._parse_vit_scores(vit_scores)
                primary = max(distribution.items(), key=lambda x: x[1])[0]
                conf = distribution[primary]
                # High threshold when no face detector anchor is found
                if conf >= 0.55:
                    return {
                        "detected": True,
                        "primary_emotion": primary,
                        "confidence": round(conf, 4),
                        "distribution": distribution,
                        "face_box": (0, 0, rgb_frame.shape[1], rgb_frame.shape[0]),
                        "annotated_frame": rgb_frame,
                        "cropped_face": rgb_frame,
                        "error": None
                    }
            except Exception:
                pass
        return self._empty_result(error="No face detected in frame. Please center your face in good lighting.")

    def _parse_vit_scores(self, vit_scores: list) -> Dict[str, float]:
        """Maps ViT emotion classification scores into normalized canonical distribution."""
        scores = {e: 0.005 for e in EMOTIONS}
        for item in vit_scores:
            label = item["label"].lower()
            canonical = VIT_EMOTION_MAP.get(label, "neutral")
            prob = float(item["score"])
            scores[canonical] = scores.get(canonical, 0.0) + prob

        # Add chill/neutral balance
        if scores.get("joy", 0) > 0.4:
            scores["chill"] += scores["joy"] * 0.25
        elif scores.get("neutral", 0) > 0.4:
            scores["chill"] += scores["neutral"] * 0.40

        total = sum(scores.values())
        return {k: round(v / total, 4) for k, v in scores.items()}

    def _fallback_geometric_analysis(self, face_gray: np.ndarray) -> Dict[str, float]:
        """Geometric fallback if neural ViT is unavailable."""
        scores = {e: 0.05 for e in EMOTIONS}
        h, w = face_gray.shape[:2]
        lower_face = face_gray[int(h * 0.5):h, :]
        smiles = self.smile_cascade.detectMultiScale(lower_face, 1.4, 15)
        if len(smiles) > 0:
            scores["joy"] += 0.65
        else:
            scores["neutral"] += 0.50
            scores["chill"] += 0.30

        total = sum(scores.values())
        return {k: round(v / total, 4) for k, v in scores.items()}

    def _empty_result(self, error: str) -> Dict[str, Any]:
        """Returns neutral baseline when face is absent."""
        default_dist = {e: (0.40 if e in ["neutral", "chill"] else 0.04) for e in EMOTIONS}
        total = sum(default_dist.values())
        return {
            "detected": False,
            "primary_emotion": "neutral",
            "confidence": 0.0,
            "distribution": {k: round(v / total, 4) for k, v in default_dist.items()},
            "face_box": None,
            "annotated_frame": None,
            "cropped_face": None,
            "error": error
        }

face_detector = FaceEmotionDetector()

def analyze_face_emotion(frame: Optional[np.ndarray]) -> Dict[str, Any]:
    """Convenience functional wrapper."""
    return face_detector.analyze_frame(frame)