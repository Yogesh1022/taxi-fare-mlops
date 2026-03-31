"""Pydantic schemas for API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaxiFareRequest(BaseModel):
    """Schema for taxi fare prediction request."""

    trip_distance: float = Field(..., gt=0, description="Distance in miles")
    fare_amount: float = Field(..., ge=0, description="Base fare")
    extra: float = Field(default=0, ge=0, description="Extra charges")
    mta_tax: float = Field(default=0.5, ge=0, description="MTA tax")
    tolls_amount: float = Field(default=0, ge=0, description="Tolls")
    surcharge: float = Field(default=0, ge=0, description="Surcharge")


class TaxiFarePrediction(BaseModel):
    """Schema for prediction response."""

    predicted_total_amount: float = Field(..., description="Predicted total fare")
    model_version: str = Field(..., description="Version of model used")
    confidence: float | None = Field(None, description="Prediction confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
