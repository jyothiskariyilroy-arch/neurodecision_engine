"""
Neuro Interpreter
-----------------
Maps raw brain region activations → 5 core business metrics.

Mapping logic:
  - Visual cortex         → Attention (visual salience)
  - Broca + Wernicke      → Clarity (language processing)
  - Prefrontal cortex     → Cognitive Load (executive function)
  - Nucleus accumbens + Amygdala → Engagement (reward + emotion)
  - Prefrontal + Anterior Cingulate + Hippocampus → Decision Readiness

Each metric uses a weighted mean of contributing regions.
Weights are tunable via REGION_WEIGHTS for future calibration.
"""

REGION_WEIGHTS: dict[str, dict[str, float]] = {
    "attention": {
        "visual_cortex": 0.60,
        "anterior_cingulate": 0.25,
        "motor_cortex": 0.15,
    },
    "engagement": {
        "nucleus_accumbens": 0.45,
        "amygdala": 0.35,
        "insula": 0.20,
    },
    "cognitive_load": {
        "prefrontal_cortex": 0.55,
        "anterior_cingulate": 0.30,
        "hippocampus": 0.15,
    },
    "clarity": {
        "broca_area": 0.50,
        "wernicke_area": 0.40,
        "prefrontal_cortex": 0.10,
    },
    "decision_readiness": {
        "prefrontal_cortex": 0.40,
        "anterior_cingulate": 0.30,
        "hippocampus": 0.20,
        "nucleus_accumbens": 0.10,
    },
}

BRAIN_INSIGHT_TEMPLATES = {
    "visual_cortex": "Visual salience and first-impression capture",
    "prefrontal_cortex": "Executive reasoning and decision-making control",
    "broca_area": "Language production and message articulation",
    "wernicke_area": "Language comprehension and semantic clarity",
    "amygdala": "Emotional resonance and threat/reward signalling",
    "hippocampus": "Memory encoding and recall likelihood",
    "anterior_cingulate": "Conflict monitoring and decision confidence",
    "nucleus_accumbens": "Reward anticipation and motivational drive",
    "insula": "Interoceptive awareness and gut-response",
    "motor_cortex": "Action preparation and behavioural intent",
}


def interpret(activations: dict[str, float]) -> dict:
    """
    Convert raw brain activations into structured neuro metrics.
    Returns metrics (0–100 scale) + brain-level insight annotations.
    """
    metrics = _compute_metrics(activations)
    conversion = _estimate_conversion(metrics)
    insights = _generate_insights(activations)

    return {
        "metrics": {**metrics, "conversion_likelihood": conversion},
        "brain_insights": insights,
    }


def _compute_metrics(activations: dict[str, float]) -> dict[str, float]:
    results = {}
    for metric, weights in REGION_WEIGHTS.items():
        weighted_sum = sum(
            activations.get(region, 0.5) * weight
            for region, weight in weights.items()
        )
        results[metric] = round(weighted_sum * 100, 2)
    return results


def _estimate_conversion(metrics: dict[str, float]) -> float:
    """
    Conversion likelihood = weighted blend of metrics most predictive
    of real-world decision action.
    Based on neuromarketing research weighting:
      - Decision Readiness (0.35)
      - Engagement (0.30)
      - Clarity (0.20)
      - Attention (0.15)
    Cognitive Load is inversely weighted (lower load = easier decision).
    """
    raw = (
        metrics["decision_readiness"] * 0.35
        + metrics["engagement"] * 0.30
        + metrics["clarity"] * 0.20
        + metrics["attention"] * 0.15
        - (metrics["cognitive_load"] - 50) * 0.10
    )
    return round(max(0, min(100, raw)), 2)


def _generate_insights(activations: dict[str, float]) -> list[dict]:
    insights = []
    sorted_regions = sorted(activations.items(), key=lambda x: x[1], reverse=True)

    for region, activation in sorted_regions[:6]:
        insights.append({
            "region": region.replace("_", " ").title(),
            "activation": round(activation * 100, 1),
            "interpretation": BRAIN_INSIGHT_TEMPLATES.get(region, "Neural activity detected"),
        })
    return insights
