from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, StrategyReport
from app.tribe.wrapper import run_tribe_inference
from app.interpreter.neuro_interpreter import interpret
from app.decision.comparison_engine import compare
from app.report.report_builder import build_report

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=StrategyReport)
async def analyze(request: AnalyzeRequest) -> StrategyReport:
    """
    Main pipeline endpoint.
    Accepts two strategies and returns a full neuro-decision report.
    """
    if not request.strategy_a.strip() or not request.strategy_b.strip():
        raise HTTPException(status_code=422, detail="Both strategies must be non-empty")

    try:
        # 1. TRIBE inference
        activations_a = run_tribe_inference(request.strategy_a)
        activations_b = run_tribe_inference(request.strategy_b)

        # 2. Neuro interpretation
        interpreted_a = interpret(activations_a)
        interpreted_b = interpret(activations_b)

        # 3. Strategy comparison
        comparison = compare(interpreted_a, interpreted_b)

        # 4. Report assembly
        report = build_report(
            interpreted_a,
            interpreted_b,
            comparison,
            include_swot=request.include_swot,
        )

        return StrategyReport(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
