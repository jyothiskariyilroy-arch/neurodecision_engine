"""
Report Builder
--------------
Assembles the final structured report from all pipeline outputs.
Produces a clean, structured dict ready for JSON serialisation.
"""

from app.report.swot import generate_swot


def build_report(
    interpreted_a: dict,
    interpreted_b: dict,
    comparison: dict,
    include_swot: bool = False,
) -> dict:
    report = {
        "winner": comparison["winner"],
        "confidence": comparison["confidence"],
        "winning_strategy": _winner_label(comparison["winner"]),
        "metrics_a": interpreted_a["metrics"],
        "metrics_b": interpreted_b["metrics"],
        "brain_insights": interpreted_a["brain_insights"],
        "business_translation": comparison["business_translation"],
        "tradeoffs": comparison["tradeoffs"],
        "improvement_suggestions": comparison["improvement_suggestions"],
    }

    if include_swot:
        report["swot"] = {
            "strategy_a": generate_swot(interpreted_a["metrics"], "A"),
            "strategy_b": generate_swot(interpreted_b["metrics"], "B"),
        }

    return report


def _winner_label(winner: str) -> str:
    return {
        "A": "Strategy A wins — stronger neuro-response profile",
        "B": "Strategy B wins — stronger neuro-response profile",
        "TIE": "No clear winner — strategies perform at parity",
    }.get(winner, "Inconclusive")
