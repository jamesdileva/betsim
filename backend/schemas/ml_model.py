from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MlModelCreate(BaseModel):
    id: str = Field(max_length=100)
    name: str | None = None
    version: str | None = None
    training_dataset: str | None = None
    features_used: dict | list | None = None
    accuracy: float | None = None
    calibration_score: float | None = None
    roi: float | None = None
    cross_validation: dict | list | None = None
    notes: str | None = None
    is_production: bool = False
    is_archived: bool = False
    model_path: str | None = None


class MlModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str | None
    version: str | None
    trained_at: datetime | None
    accuracy: float | None
    calibration_score: float | None
    roi: float | None
    is_production: bool
    is_archived: bool
    created_at: datetime


class ModelPredictionCreate(BaseModel):
    model_id: str
    game_id: str
    predicted_probability: float
    confidence: float | None = None
    fair_odds_decimal: float | None = None
    ev: float | None = None


class ModelPredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: str
    game_id: str
    predicted_probability: float | None
    confidence: float | None
    fair_odds_decimal: float | None
    ev: float | None
    created_at: datetime


class SystemPlayResultCreate(BaseModel):
    simulation_run_id: int | None = None
    stated_probability: float
    actual_win_rate: float
    calibration_error: float | None = None
    calibration_status: str | None = None
    confidence_interval_low: float | None = None
    confidence_interval_high: float | None = None
    recommendation: str | None = None


class SystemPlayResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    simulation_run_id: int | None
    stated_probability: float | None
    actual_win_rate: float | None
    calibration_error: float | None
    calibration_status: str | None
    confidence_interval_low: float | None
    confidence_interval_high: float | None
    recommendation: str | None
    created_at: datetime
