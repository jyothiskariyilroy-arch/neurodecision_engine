from pydantic import BaseModel, Field
from typing import Optional, Literal


class AnalyzeRequest(BaseModel):
    strategy_a: str = Field(..., description="Text, image URL, or video URL for Strategy A")
    strategy_b: str = Field(..., description="Text, image URL, or video URL for Strategy B")
    include_swot: bool = Field(default=False, description="Include SWOT analysis in report")
    audience_segment: Optional[str] = Field(default=None, description="Target audience for segmentation (future)")


class NeuroMetrics(BaseModel):
    attention: float = Field(..., ge=0, le=100)
    engagement: float = Field(..., ge=0, le=100)
    cognitive_load: float = Field(..., ge=0, le=100)
    clarity: float = Field(..., ge=0, le=100)
    decision_readiness: float = Field(..., ge=0, le=100)
    conversion_likelihood: float = Field(..., ge=0, le=100)


class BrainInsight(BaseModel):
    region: str
    activation: float
    interpretation: str


class TradeOff(BaseModel):
    dimension: str
    strategy_a_advantage: str
    strategy_b_advantage: str


class SwotAnalysis(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]


class StrategyReport(BaseModel):
    winner: Literal["A", "B", "TIE"]
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    winning_strategy: str
    metrics_a: NeuroMetrics
    metrics_b: NeuroMetrics
    brain_insights: list[BrainInsight]
    business_translation: dict[str, str]
    tradeoffs: list[TradeOff]
    improvement_suggestions: dict[str, list[str]]
    swot: Optional[dict[str, SwotAnalysis]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
