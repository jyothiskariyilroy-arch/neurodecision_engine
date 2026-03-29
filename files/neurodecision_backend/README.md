# NeuroDecision Engine

> Brain-response simulation for strategy comparison

## Architecture

```
INPUT → TRIBE → Brain Signals → Neuro Interpreter → Decision Engine → Report
```

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API

### POST /api/analyze

```json
{
  "strategy_a": "Launch with a bold video testimonial campaign",
  "strategy_b": "Launch with a targeted email sequence and webinar",
  "include_swot": true
}
```

**Response:**
```json
{
  "winner": "A",
  "confidence": 78.4,
  "winning_strategy": "Strategy A wins — stronger neuro-response profile",
  "metrics_a": { "attention": 82.1, "engagement": 75.3, ... },
  "metrics_b": { "attention": 61.4, "engagement": 68.9, ... },
  "brain_insights": [...],
  "business_translation": {...},
  "tradeoffs": [...],
  "improvement_suggestions": {...},
  "swot": {...}
}
```

## Plugging in Real TRIBE

In `app/tribe/wrapper.py`:

1. Set `TRIBE_MODEL_PATH` env var to your model weights directory
2. Implement `_real_inference()` — convert preprocessed input → TRIBE tensor → float dict
3. Replace `_mock_inference()` call in `run_tribe_inference()` with `_real_inference()`

## Module Map

| Module | Responsibility | Swap Cost |
|---|---|---|
| `tribe/wrapper.py` | TRIBE inference | Low — clean interface |
| `interpreter/neuro_interpreter.py` | Region → metric mapping | Low — weights in `REGION_WEIGHTS` dict |
| `decision/comparison_engine.py` | A vs B scoring | Medium — rule-based, auditable |
| `report/report_builder.py` | Report assembly | Low — pure aggregation |
| `report/swot.py` | SWOT generation | Low — threshold-based rules |

## Roadmap

- [ ] Real TRIBE v2 integration
- [ ] Audience segmentation (by age/persona)
- [ ] Video/image input preprocessing
- [ ] Real-time WebSocket streaming for live simulation
- [ ] Historical comparison dashboard
