from __future__ import annotations

from typing import Any


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def detect_undertone(a_channel: float, b_channel: float) -> tuple[str, float, float]:
    # OpenCV LAB uses 128-centered A/B channels.
    a_delta = a_channel - 128.0
    b_delta = b_channel - 128.0

    undertone_score = b_delta - a_delta
    neutral_margin = 6.0

    if abs(undertone_score) <= neutral_margin:
        undertone = "neutral"
    elif undertone_score > 0:
        undertone = "warm"
    else:
        undertone = "cool"

    confidence = _clamp(abs(undertone_score) / 30.0, 0.0, 1.0)
    return undertone, confidence, undertone_score


def detect_contrast(l_mean: float, l_std: float) -> tuple[str, float]:
    # Proxy contrast from luminance spread within skin pixels.
    if l_std >= 18.0:
        contrast = "high"
        confidence = _clamp((l_std - 18.0) / 14.0 + 0.6, 0.0, 1.0)
    elif l_std >= 10.0:
        contrast = "medium"
        confidence = _clamp(0.5 + abs(l_std - 14.0) / 16.0, 0.0, 1.0)
    else:
        contrast = "low"
        confidence = _clamp((10.0 - l_std) / 12.0 + 0.55, 0.0, 1.0)

    return contrast, confidence


def detect_skin_tone_bucket(l_mean: float) -> str:
    # Buckets aligned to project plan categories.
    if l_mean >= 185.0:
        return "fair"
    if l_mean >= 150.0:
        return "medium"
    if l_mean >= 120.0:
        return "olive"
    return "deep"


def build_color_profile(lab_values: dict[str, Any]) -> dict[str, Any]:
    l_mean = float(lab_values["L"])
    a_mean = float(lab_values["A"])
    b_mean = float(lab_values["B"])
    l_std = float(lab_values.get("L_std", 0.0))

    undertone, undertone_confidence, undertone_score = detect_undertone(a_mean, b_mean)
    contrast, contrast_confidence = detect_contrast(l_mean, l_std)
    skin_tone_bucket = detect_skin_tone_bucket(l_mean)

    # Determine Color Season
    if undertone == "warm":
        season = "Autumn" if contrast == "high" else "Spring"
    else:
        season = "Winter" if contrast == "high" else "Summer"

    return {
        "profile_version": "1.1.0",
        "skin_tone_bucket": skin_tone_bucket,
        "undertone": undertone,
        "contrast": contrast,
        "season": season,
        "tone_score": f"{skin_tone_bucket.capitalize()} / {undertone.capitalize()}",
        "confidence": {
            "undertone": round(undertone_confidence, 3),
            "contrast": round(contrast_confidence, 3),
        },
        "skin_lab": {
            "L": round(l_mean, 3),
            "A": round(a_mean, 3),
            "B": round(b_mean, 3),
            "L_std": round(l_std, 3),
        },
        # Legacy-compatible fields
        "skin_L": round(l_mean, 3),
        "skin_A": round(a_mean, 3),
        "skin_B": round(b_mean, 3),
        "diagnostics": {
            "undertone_score": round(undertone_score, 3),
            "pixel_count": int(lab_values.get("pixel_count", 0)),
            "face_detected": bool(lab_values.get("face_detected", False)),
            "extraction_method": str(lab_values.get("method", "unknown")),
            "quality_flags": list(lab_values.get("quality_flags", [])),
        },
    }
