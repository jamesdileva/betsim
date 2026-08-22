from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MlModel(Base):
    """Model registry: every trained model version with metrics and status."""

    __tablename__ = "ml_models"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100), index=True)
    version: Mapped[str | None] = mapped_column(String(20))
    trained_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    training_dataset: Mapped[str | None] = mapped_column(String(100))
    features_used: Mapped[dict | list | None] = mapped_column(JSON)
    accuracy: Mapped[float | None] = mapped_column(Float)
    calibration_score: Mapped[float | None] = mapped_column(Float)
    roi: Mapped[float | None] = mapped_column(Float)
    cross_validation: Mapped[dict | list | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    model_path: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    predictions: Mapped[list["ModelPrediction"]] = relationship(
        "ModelPrediction", back_populates="model"
    )
    backtest_results: Mapped[list["BacktestResult"]] = relationship(
        "BacktestResult", back_populates="model"
    )
    evaluations: Mapped[list["ModelEvaluation"]] = relationship(
        "ModelEvaluation", back_populates="model"
    )


class ModelPrediction(Base):
    """Every prediction made by every model version for every game."""

    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[str] = mapped_column(ForeignKey("ml_models.id"), index=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), index=True)
    predicted_probability: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float)
    fair_odds_decimal: Mapped[float | None] = mapped_column(Float)
    ev: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    model: Mapped["MlModel"] = relationship("MlModel", back_populates="predictions")
    game: Mapped["Game"] = relationship(  # noqa: F821
        "Game", back_populates="predictions"
    )


class BacktestResult(Base):
    """Historical replay: prediction vs. actual outcome per game."""

    __tablename__ = "backtest_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[str] = mapped_column(ForeignKey("ml_models.id"), index=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), index=True)
    predicted_probability: Mapped[float | None] = mapped_column(Float)
    actual_outcome: Mapped[bool | None]
    edge: Mapped[float | None] = mapped_column(Float)
    roi: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    model: Mapped["MlModel"] = relationship("MlModel", back_populates="backtest_results")
    game: Mapped["Game"] = relationship(  # noqa: F821
        "Game", back_populates="backtest_results"
    )


class ModelEvaluation(Base):
    """Periodic model performance evaluation on backtest data."""

    __tablename__ = "model_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[str] = mapped_column(ForeignKey("ml_models.id"), index=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    accuracy: Mapped[float | None] = mapped_column(Float)
    calibration_error: Mapped[float | None] = mapped_column(Float)
    avg_roi: Mapped[float | None] = mapped_column(Float)
    brier_score: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    model: Mapped["MlModel"] = relationship("MlModel", back_populates="evaluations")
