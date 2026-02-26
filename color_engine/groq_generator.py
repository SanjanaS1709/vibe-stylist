from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", os.getenv("TEMPERATURE", "0.7")))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", os.getenv("MAX_TOKENS", "1200")))


def _groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")
    return Groq(api_key=api_key)


def _build_prompt(profile: dict[str, Any], context: dict[str, Any] | None = None) -> str:
    user_segment = (context or {}).get("user_segment", "college_student")
    user_mood = (context or {}).get("mood", "not_provided")
    user_occasion = (context or {}).get("occasion", "not_provided")
    user_gender = (context or {}).get("gender", "not_provided")
    campus_style = (context or {}).get("campus_style", "not_provided")
    budget_tier = (context or {}).get("budget_tier", "not_provided")
    student_year = (context or {}).get("student_year", "not_provided")
    season = (context or {}).get("season", "not_provided")

    return f"""
You are a professional fashion stylist for college students.

You must use only the computed profile and user context below.
Do not perform pixel math, image processing, face detection, or database logic.

Structured profile:
{json.dumps(profile, indent=2)}

User context:
- user_segment: {user_segment}
- gender: {user_gender}
- mood: {user_mood}
- occasion: {user_occasion}
- campus_style: {campus_style}
- budget_tier: {budget_tier}
- student_year: {student_year}
- season: {season}

Return STRICT JSON only with this exact shape:
{{
  "summary": "one short paragraph",
  "palettes": [
    {{
      "name": "palette name",
      "primary": "color name",
      "secondary": "color name",
      "accent": "color name",
      "hex": {{
        "primary": "#RRGGBB",
        "secondary": "#RRGGBB",
        "accent": "#RRGGBB"
      }},
      "campus_fit": "where to wear this on campus",
      "affordability_tip": "practical low-cost styling tip",
      "why_it_works": "short explanation"
    }}
  ],
  "style_guidance": {{
    "gender_alignment_note": "how recommendations reflect selected gender preference",
    "dress_codes": [
      {{
        "code": "formal|business|casual|party",
        "top": "recommended top",
        "bottom": "recommended bottom",
        "shoes": "recommended shoes",
        "why": "short reason"
      }}
    ],
    "hairstyle": {{
      "recommendation": "hairstyle direction",
      "maintenance_tip": "simple maintenance tip"
    }},
    "accessories": [
      "item 1",
      "item 2",
      "item 3"
    ]
  }},
  "styling_notes": [
    "note 1",
    "note 2"
  ]
}}

Rules:
- Provide exactly 3 palettes.
- Provide exactly 4 dress_codes in this order: formal, business, casual, party.
- Keep everything practical for college students.
- Include budget-aware advice.
- Output JSON only. No markdown.
""".strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Model response does not contain a JSON object.")
        return json.loads(text[start : end + 1])


def _normalize_palettes(payload: dict[str, Any]) -> dict[str, Any]:
    palettes_raw = payload.get("palettes")
    if not isinstance(palettes_raw, list):
        palettes_raw = []

    res = {}
    categories = ["daily", "college", "evening"]
    for i, palette in enumerate(palettes_raw[:3]):
        cat = categories[i] if i < len(categories) else f"palette_{i}"
        
        hex_map = palette.get("hex", {})
        colors = [
            {"name": palette.get("primary", "Primary"), "hex": hex_map.get("primary", "#000000")},
            {"name": palette.get("secondary", "Secondary"), "hex": hex_map.get("secondary", "#000000")},
            {"name": palette.get("accent", "Accent"), "hex": hex_map.get("accent", "#000000")}
        ]

        res[cat] = {
            "colors": colors,
            "reasoning": palette.get("why_it_works", "")
        }
    return res


def _normalize_style_guidance(payload: dict[str, Any]) -> dict[str, Any]:
    style = payload.get("style_guidance", {})
    if not isinstance(style, dict):
        style = {}

    return {
        "overview": str(payload.get("summary", "Your custom style guidelines.")),
        "gender_alignment_note": str(style.get("gender_alignment_note", "")),
        "accessories": style.get("accessories", [])
    }


def _normalize_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "palettes": _normalize_palettes(payload),
        "style_guidance": _normalize_style_guidance(payload),
    }


def _fallback_style_guidance(gender: str) -> dict[str, Any]:
    gender_note = (
        f"Recommendations were adapted for {gender} preference."
        if gender
        else "Recommendations are balanced and gender-flexible."
    )
    return {
        "gender_alignment_note": gender_note,
        "dress_codes": [
            {
                "code": "formal",
                "top": "Solid blazer with light shirt",
                "bottom": "Tailored trousers",
                "shoes": "Polished loafers or clean heels",
                "why": "Creates a sharp profile for interviews and formal presentations.",
            },
            {
                "code": "business",
                "top": "Smart shirt or neat knit top",
                "bottom": "Straight-fit chinos or ankle trousers",
                "shoes": "Minimal sneakers or loafers",
                "why": "Professional enough for campus office interactions.",
            },
            {
                "code": "casual",
                "top": "Breathable tee or casual kurti/shirt",
                "bottom": "Denim or relaxed chinos",
                "shoes": "Comfort sneakers",
                "why": "Comfort-driven look for daily classes and commute.",
            },
            {
                "code": "party",
                "top": "Statement shirt/top in accent tone",
                "bottom": "Dark denim or sleek pants",
                "shoes": "Clean high-top sneakers or dress shoes",
                "why": "Keeps style expressive without losing campus practicality.",
            },
        ],
        "hairstyle": {
            "recommendation": "Low-maintenance textured style aligned with face shape.",
            "maintenance_tip": "Use lightweight serum and schedule one trim every 5 to 7 weeks.",
        },
        "accessories": [
            "Minimal watch",
            "Simple chain or pendant",
            "Campus-ready backpack in neutral color",
        ],
    }


def _fallback_payload(profile: dict[str, Any], context: dict[str, Any], reason: str) -> dict[str, Any]:
    undertone = str(profile.get("undertone", "neutral"))
    gender = str(context.get("gender", "")).strip()

    if undertone == "warm":
        base = [
            (
                "Earth Balance",
                "Terracotta",
                "Camel",
                "Sage",
                "#C76A4A",
                "#C19A6B",
                "#7B9B6A",
                "Everyday classes and campus cafe meetups",
                "Pair one accent item with repeat basics you already own.",
            ),
            (
                "Golden Evening",
                "Mustard",
                "Warm Beige",
                "Deep Teal",
                "#D4A017",
                "#D2B48C",
                "#1F5F61",
                "College fest evenings and informal events",
                "Buy secondary layers from affordable campus markets.",
            ),
            (
                "Rustic Sharp",
                "Rust",
                "Olive",
                "Cream",
                "#B7410E",
                "#6B8E23",
                "#F5F5DC",
                "Presentation days and project demos",
                "Reuse neutral trousers and rotate only tops.",
            ),
        ]
    elif undertone == "cool":
        base = [
            (
                "Urban Cool",
                "Navy",
                "Slate Gray",
                "Icy Blue",
                "#1E3A5F",
                "#708090",
                "#A7C7E7",
                "Lectures, library, and daily commute",
                "Start with one navy base layer and mix with existing denim.",
            ),
            (
                "Berry Minimal",
                "Burgundy",
                "Charcoal",
                "Dusty Rose",
                "#7A1F3D",
                "#36454F",
                "#C08081",
                "Club meetings and campus socials",
                "Use accessories for color pop instead of full outfit changes.",
            ),
            (
                "Monochrome Pop",
                "Black",
                "Steel",
                "Cobalt",
                "#1F1F1F",
                "#71797E",
                "#0047AB",
                "Seminars and internship interviews",
                "Invest in one quality black staple and style it repeatedly.",
            ),
        ]
    else:
        base = [
            (
                "Neutral Core",
                "Taupe",
                "Soft White",
                "Forest Green",
                "#8B7D6B",
                "#F8F8F2",
                "#2E5E4E",
                "Long campus days and practical daily wear",
                "Pick machine-wash basics in neutral shades.",
            ),
            (
                "Balanced Classic",
                "Navy",
                "Stone",
                "Muted Coral",
                "#203A5F",
                "#BFA88F",
                "#D6816A",
                "Group presentations and networking events",
                "Use thrifted layers to keep costs controlled.",
            ),
            (
                "Clean Contrast",
                "Mocha",
                "Sand",
                "Denim Blue",
                "#6F4E37",
                "#C2B280",
                "#4F6D8A",
                "Weekend hangouts and casual campus plans",
                "Repeat one denim outer layer across multiple outfits.",
            ),
        ]

    palettes = []
    for name, primary, secondary, accent, h1, h2, h3, campus_fit, affordability_tip in base:
        palettes.append(
            {
                "name": name,
                "primary": primary,
                "secondary": secondary,
                "accent": accent,
                "hex": {"primary": h1, "secondary": h2, "accent": h3},
                "campus_fit": campus_fit,
                "affordability_tip": affordability_tip,
                "why_it_works": (
                    f"Fallback palette tuned for {undertone} undertone and student-friendly wearability."
                ),
            }
        )

    return {
        "summary": "Fallback campus-friendly style response generated because live Groq response was unavailable.",
        "palettes": palettes,
        "style_guidance": _fallback_style_guidance(gender),
        "styling_notes": [
            "Palettes are tuned for college-student daily use.",
            "Use fallback only when API is unavailable.",
            f"Failure reason: {reason}",
        ],
        "raw_text": "",
    }


def generate_style_package(
    profile: dict[str, Any], context: dict[str, Any] | None = None
) -> dict[str, Any]:
    context = context or {}
    prompt = _build_prompt(profile=profile, context=context)

    try:
        client = _groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )
        content = response.choices[0].message.content or ""
        parsed = _extract_json_object(content)
        normalized = _normalize_response(parsed)
        normalized["raw_text"] = content
        return normalized
    except Exception as exc:
        return _fallback_payload(profile=profile, context=context, reason=str(exc))


def generate_palettes(profile: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    # Backward-compatible alias.
    return generate_style_package(profile=profile, context=context)
