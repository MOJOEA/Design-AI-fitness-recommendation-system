from __future__ import annotations

from fastapi import FastAPI

from .catalog import load_exercises
from .parser import parse_intent
from .recommender import recommend
from .schemas import RecommendationRequest, RecommendationResponse

app = FastAPI(
    title="Personalized Fitness AI Recommendation System",
    version="0.1.0",
    description="Deterministic zero-hallucination exercise recommendations backed by a curated dataset.",
)

CATALOG = load_exercises()


@app.get("/health")
def health() -> dict[str, int | str]:
    return {"status": "ok", "exercise_count": len(CATALOG)}


@app.post("/recommendations", response_model=RecommendationResponse)
def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    intent = parse_intent(request.message, CATALOG)
    return recommend(CATALOG, intent, max_results=request.max_results)