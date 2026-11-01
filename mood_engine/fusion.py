"""
Confidence-weighted Multimodal Emotion Fusion combining NLP semantics and Facial Affect.
"""

from typing import Dict, Any, Optional
from config.settings import EMOTIONS, DEFAULT_FUSION_WEIGHTS
from utils.logging_config import logger

def fuse_multimodal_emotions(
    text_result: Dict[str, Any],
    face_result: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Intelligently fuses textual and facial emotion signals using confidence weighting.

    Equation:
        score(e) = (w_text * P_text(e) * C_text) + (w_face * P_face(e) * C_face)

    Adapts gracefully to:
        - Multimodal mode (both text and face signals present)
        - Text-only mode (no camera frame / no face detected)
        - Face-only mode (empty text box / face detected)
        - Baseline mode (neither signal provided)
    """
    w = weights or DEFAULT_FUSION_WEIGHTS
    w_text = w.get("text_weight", 0.60)
    w_face = w.get("face_weight", 0.40)

    has_text = text_result.get("success", False) and bool(text_result.get("raw_text"))
    has_face = face_result.get("detected", False)

    text_dist = text_result.get("distribution", {})
    text_conf = text_result.get("confidence", 0.0)
    text_prim = text_result.get("primary_emotion", "neutral")

    face_dist = face_result.get("distribution", {})
    face_conf = face_result.get("confidence", 0.0)
    face_prim = face_result.get("primary_emotion", "neutral")

    fused_scores = {e: 0.0 for e in EMOTIONS}
    mode = "baseline"
    reasoning = ""

    if has_text and has_face:
        mode = "multimodal"
        # Dynamic weighting based on mutual agreement
        agreement_boost = 1.25 if text_prim == face_prim else 1.0

        for emo in EMOTIONS:
            pt = text_dist.get(emo, 0.0)
            pf = face_dist.get(emo, 0.0)
            fused_scores[emo] = (w_text * pt * text_conf) + (w_face * pf * face_conf)
            if emo == text_prim == face_prim:
                fused_scores[emo] *= agreement_boost

        if text_prim == face_prim:
            reasoning = (
                f"High consensus: Both your text input and facial expression converge strongly on '{text_prim.upper()}' "
                f"(Text conf: {text_conf:.0%}, Face conf: {face_conf:.0%})."
            )
        else:
            reasoning = (
                f"Multimodal balance: Text sentiment leaned toward '{text_prim.upper()}' ({text_conf:.0%}) "
                f"while facial expression indicated '{face_prim.upper()}' ({face_conf:.0%}). "
                f"Confidence-weighted fusion synthesized these into a unified state."
            )

    elif has_text and not has_face:
        mode = "text_only"
        for emo in EMOTIONS:
            fused_scores[emo] = text_dist.get(emo, 0.0) * max(0.2, text_conf)
        face_err = face_result.get("error") or "No camera snapshot supplied"
        reasoning = (
            f"Text-guided analysis: Analyzed textual semantics ({text_conf:.0%} confidence on '{text_prim.upper()}'). "
            f"Camera was unavailable or unused ({face_err})."
        )

    elif not has_text and has_face:
        mode = "face_only"
        for emo in EMOTIONS:
            fused_scores[emo] = face_dist.get(emo, 0.0) * max(0.2, face_conf)
        reasoning = (
            f"Vision-guided analysis: Analyzed facial features ({face_conf:.0%} confidence on '{face_prim.upper()}'). "
            f"No textual description was provided."
        )

    else:
        mode = "baseline"
        fused_scores["neutral"] = 0.55
        fused_scores["chill"] = 0.45
        reasoning = (
            "Neutral baseline: Neither text nor facial cues were detected. "
            "System activated default calm equilibrium mode."
        )

    # Normalize fused scores
    total = sum(fused_scores.values())
    if total <= 0:
        total = 1.0
        fused_scores["neutral"] = 1.0

    normalized_dist = {k: round(v / total, 4) for k, v in fused_scores.items()}
    fused_primary = max(normalized_dist.items(), key=lambda x: x[1])[0]
    final_conf = normalized_dist[fused_primary]

    logger.info(f"Fusion complete [{mode}]: {fused_primary} ({final_conf:.2%})")

    return {
        "fused_emotion": fused_primary,
        "confidence": round(final_conf, 4),
        "distribution": normalized_dist,
        "mode": mode,
        "reasoning": reasoning,
        "text_primary": text_prim if has_text else None,
        "face_primary": face_prim if has_face else None,
    }