"""FastAPI application for predictions."""

import os
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Taxi Fare Prediction API", version="0.1.0", description="Real-time taxi fare predictions"
)


class PredictionRequest(BaseModel):
    """Request schema for predictions."""

    trip_distance: float
    fare_amount: float
    extra: float
    tip_amount: float


class PredictionResponse(BaseModel):
    """Response schema for predictions."""

    predicted_total_amount: float
    model_version: str
    timestamp: datetime


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Make a prediction."""
    # TODO: Implement prediction logic
    return PredictionResponse(
        predicted_total_amount=10.0, model_version="0.1.0", timestamp=datetime.now()
    )


@app.get("/metadata")
def metadata():
    """Get model metadata."""
    return {
        "name": "taxi-fare-prediction",
        "version": "0.1.0",
        "algorithm": "ensemble",
        "features": [],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("API_HOST", "127.0.0.1"), port=8000)
