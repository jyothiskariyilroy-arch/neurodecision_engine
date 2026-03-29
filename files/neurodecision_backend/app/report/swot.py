"""
SWOT Generator
--------------
Derives SWOT from neuro-metric profiles.
Strengths and Weaknesses come from the metrics directly.
Opportunities and Threats are strategic inferences.
"""

SWOT_RULES = {
    "strengths": {
        "attention": (70, "High visual salience — captures attention quickly"),
        "engagement": (70, "Strong emotional resonance — audience connects deeply"),
        "clarity": (75, "Clear and direct message — minimal cognitive effort"),
        "decision_readiness": (70, "Strong purchase intent signals"),
        "conversion_likelihood": (70, "High predicted conversion rate"),
    },
    "weaknesses": {
        "attention": (50, "Low visual impact — risk of being ignored"),
        "engagement": (50, "Weak emotional connection — fails to motivate"),
        "clarity": (55, "Message is unclear — may confuse audience"),
        "cognitive_load": (65, "High mental load — audience may disengage"),
        "decision_readiness": (55, "Weak decision triggers — won't drive action"),
    },
    "opportunities": [
        "Refining the visual hierarchy can amplify attention gains",
        "A/B testing headline copy could yield 15–30% clarity improvements",
        "Adding social proof may significantly boost decision readiness",
        "Simplifying the CTA reduces cognitive load and increases conversion",
    ],
    "threats": [
        "High cognitive load risks audience drop-off before conversion",
        "Low engagement may make the strategy forgettable in competitive contexts",
        "Without clear differentiation, the message may be lost in ad noise",
        "Sustained low clarity could damage brand perception over time",
    ],
}


def generate_swot(metrics: dict, strategy_label: str) -> dict:
    strengths = [
        msg for metric, (threshold, msg) in SWOT_RULES["strengths"].items()
        if metrics.get(metric, 0) >= threshold
    ]

    weaknesses = [
        msg for metric, (threshold, msg) in SWOT_RULES["weaknesses"].items()
        if metrics.get(metric, 100) < threshold
    ]

    return {
        "strengths": strengths or ["No dominant strengths identified"],
        "weaknesses": weaknesses or ["No critical weaknesses detected"],
        "opportunities": SWOT_RULES["opportunities"][:3],
        "threats": SWOT_RULES["threats"][:2],
    }
