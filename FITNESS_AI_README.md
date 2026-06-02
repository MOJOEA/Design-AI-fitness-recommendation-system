# Personalized Fitness AI Recommendation System

This module implements a zero-hallucination recommendation pipeline for the fitness use case. The LLM-facing responsibilities are intentionally isolated: parsing can be swapped for an external NLP model, and final wording can be replaced by a language model, but the catalog filtering and injury exclusions remain deterministic Python business logic.

## Architecture

1. **Input Parsing**: `fitness_ai.parser.parse_intent` converts natural language into a validated `ParsedIntent` object.
2. **Core Business Logic**: `fitness_ai.recommender.recommend` filters only rows loaded from `fitness_ai/data/exercises.csv`, then blocks any exercise whose `excluded_injuries` intersects with the parsed injuries.
3. **Structured Output**: `fitness_ai.schemas.RecommendationResponse` returns Thai natural-language guidance plus structured JSON fields for frontend consumption.

## Run locally

```bash
python -m pip install -r requirements-fitness.txt
uvicorn fitness_ai.api:app --reload
```

Then call:

```bash
curl -X POST http://127.0.0.1:8000/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"message":"อยากเล่นท้อง มีสายแรงต้าน แต่เจ็บข้อมือ", "max_results": 3}'
```

## Safety guarantee boundary

The system never creates exercise names in the recommender. Recommendations are projected from the loaded catalog only. If no safe row exists after filtering, the response contains no recommendation items and explains that the request was blocked or had no match.