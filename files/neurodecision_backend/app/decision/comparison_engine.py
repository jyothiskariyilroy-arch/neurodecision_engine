"""
Strategy Comparison Engine
---------------------------
Compares two interpreted neuro-metric profiles.
Determines winner, confidence score, trade-offs, and improvement suggestions.

Design for extensibility:
  - Weights are configurable per audience segment (future)
  - Trade-off logic is rule-based and auditable
  - Suggestions are derived from metric gaps, not hallucinated
"""

from typing import Literal

METRIC_BUSINESS_MAP = {
    "attention": "First-impression capture and ad recall",
    "engagement": "Emotional resonance and dwell time",
    "cognitive_load": "Message simplicity and comprehension speed",
    "clarity": "Brand communication effectiveness",
    "decision_readiness": "Purchase intent and call-to-action response",
    "conversion_likelihood": "Predicted real-world conversion rate",
}

IMPROVEMENT_THRESHOLDS = {
    "attention": 60,
    "engagement": 65,
    "cognitive_load": 55,
    "clarity": 70,
    "decision_readiness": 65,
    "conversion_likelihood": 60,
}

IMPROVEMENT_SUGGESTIONS = {
    "attention": [
        "Add a high-contrast visual anchor in the first 2 seconds",
        "Use motion or colour change to trigger visual saliency",
        "Reduce visual clutter — isolate the primary message",
    ],
    "engagement": [
        "Incorporate social proof or relatable protagonist",
        "Use emotionally resonant language or imagery",
        "Add a narrative arc with tension and resolution",
    ],
    "cognitive_load": [
        "Reduce message density — one core idea per screen",
        "Use bullet points or chunked information",
        "Eliminate jargon; favour concrete, simple language",
    ],
    "clarity": [
        "Lead with the benefit, not the feature",
        "Use plain-language headline with a single CTA",
        "Test readability at Flesch-Kincaid Grade 8 or below",
    ],
    "decision_readiness": [
        "Add urgency signals: scarcity, time limit, or social pressure",
        "Make the next step frictionless (one-click, pre-filled form)",
        "Use commitment-and-consistency cues early in the flow",
    ],
    "conversion_likelihood": [
        "A/B test the CTA copy — verb-first performs best",
        "Ensure value proposition is visible above the fold",
        "Reduce steps between intent and action",
    ],
}


def compare(interpreted_a: dict, interpreted_b: dict) -> dict:
    metrics_a = interpreted_a["metrics"]
    metrics_b = interpreted_b["metrics"]

    winner, confidence = _determine_winner(metrics_a, metrics_b)
    tradeoffs = _compute_tradeoffs(metrics_a, metrics_b)
    suggestions = _generate_suggestions(metrics_a, metrics_b, winner)
    business_translation = _build_business_translation(metrics_a, metrics_b, winner)

    return {
        "winner": winner,
        "confidence": confidence,
        "business_translation": business_translation,
        "tradeoffs": tradeoffs,
        "improvement_suggestions": suggestions,
    }


def _determine_winner(
    metrics_a: dict, metrics_b: dict
) -> tuple[Literal["A", "B", "TIE"], float]:
    """
    Score each strategy using weighted metric sum.
    Cognitive load is inverted: lower load = higher score.
    """
    weights = {
        "conversion_likelihood": 0.30,
        "decision_readiness": 0.25,
        "engagement": 0.20,
        "clarity": 0.15,
        "attention": 0.10,
    }

    def score(m: dict) -> float:
        cl_penalty = max(0, m["cognitive_load"] - 50) * 0.15
        return sum(m[k] * w for k, w in weights.items()) - cl_penalty

    score_a = score(metrics_a)
    score_b = score(metrics_b)
    delta = abs(score_a - score_b)
    total = score_a + score_b

    raw_confidence = round((delta / total) * 200, 1) if total > 0 else 0
    confidence = min(98.0, max(51.0, raw_confidence + 60))

    if delta < 2.0:
        return "TIE", 50.0
    elif score_a > score_b:
        return "A", confidence
    else:
        return "B", confidence


def _compute_tradeoffs(metrics_a: dict, metrics_b: dict) -> list[dict]:
    tradeoffs = []
    dimension_labels = {
        "attention": "Visual Attention",
        "engagement": "Emotional Engagement",
        "cognitive_load": "Cognitive Load",
        "clarity": "Message Clarity",
        "decision_readiness": "Decision Readiness",
    }

    for dimension, label in dimension_labels.items():
        val_a = metrics_a[dimension]
        val_b = metrics_b[dimension]
        diff = val_a - val_b

        if abs(diff) < 5:
            continue

        if dimension == "cognitive_load":
            a_adv = "Lower mental effort required" if diff < 0 else "Requires deeper processing"
            b_adv = "Lower mental effort required" if diff > 0 else "Requires deeper processing"
        else:
            a_adv = f"Stronger on {label}" if diff > 0 else f"Weaker on {label}"
            b_adv = f"Stronger on {label}" if diff < 0 else f"Weaker on {label}"

        tradeoffs.append({
            "dimension": label,
            "strategy_a_advantage": a_adv,
            "strategy_b_advantage": b_adv,
            "delta": round(abs(diff), 1),
        })

    return sorted(tradeoffs, key=lambda x: x["delta"], reverse=True)


def _generate_suggestions(
    metrics_a: dict, metrics_b: dict, winner: str
) -> dict[str, list[str]]:
    loser_metrics = metrics_b if winner == "A" else metrics_a
    loser_label = "Strategy B" if winner == "A" else "Strategy A"

    weak_dimensions = [
        dim for dim, threshold in IMPROVEMENT_THRESHOLDS.items()
        if loser_metrics.get(dim, 100) < threshold
    ]

    suggestions = {}
    for dim in weak_dimensions[:4]:
        suggestions[dim] = IMPROVEMENT_SUGGESTIONS[dim][:2]

    return {loser_label: suggestions}


def _build_business_translation(
    metrics_a: dict, metrics_b: dict, winner: str
) -> dict[str, str]:
    winner_metrics = metrics_a if winner in ("A", "TIE") else metrics_b
    return {
        metric: f"{METRIC_BUSINESS_MAP[metric]} — score: {round(winner_metrics[metric], 1)}/100"
        for metric in METRIC_BUSINESS_MAP
        if metric in winner_metrics
    }
