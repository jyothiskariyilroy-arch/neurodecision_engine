from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analyze
from app.models.schemas import HealthResponse

app = FastAPI(
    title="NeuroDecision Engine",
    description="Brain-response simulation for strategy comparison",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "operational", "version": "1.0.0"}
