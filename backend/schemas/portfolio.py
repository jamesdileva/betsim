from datetime import date as dt_date
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PortfolioItemCreate(BaseModel):
    game_id: str | None = None
    model_id: str | None = None
    confidence_level: str | None = None
    bet_type: str | None = None
    stake: float | None = None
    predicted_probability: float | None = None
    ev: float | None = None
    recommendation_stars: int | None = None


class PortfolioCreate(BaseModel):
    date: dt_date | None = None
    total_risk: float | None = None
    expected_roi: float | None = None
    kelly_exposure: float | None = None
    model_id: str | None = None
    items: list[PortfolioItemCreate] = []


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: dt_date | None
    total_risk: float | None
    expected_roi: float | None
    kelly_exposure: float | None
    model_id: str | None
    created_at: datetime


class PortfolioItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    game_id: str | None
    model_id: str | None
    confidence_level: str | None
    bet_type: str | None
    stake: float | None
    predicted_probability: float | None
    ev: float | None
    recommendation_stars: int | None
    created_at: datetime


class BacktestResultCreate(BaseModel):
    model_id: str
    game_id: str
    predicted_probability: float
    actual_outcome: bool | None = None
    edge: float | None = None
    roi: float | None = None


class BacktestResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: str
    game_id: str
    predicted_probability: float | None
    actual_outcome: bool | None
    edge: float | None
    roi: float | None
    created_at: datetime


class ModelEvaluationCreate(BaseModel):
    model_id: str
    accuracy: float | None = None
    calibration_error: float | None = None
    avg_roi: float | None = None
    brier_score: float | None = None
    notes: str | None = None


class ModelEvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: str
    evaluated_at: datetime | None
    accuracy: float | None
    calibration_error: float | None
    avg_roi: float | None
    brier_score: float | None
    notes: str | None
    created_at: datetime
