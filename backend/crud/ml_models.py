"""CRUD operations for the ML model registry and predictions."""

from sqlalchemy.orm import Session

from models import MlModel, ModelPrediction
from schemas.ml_model import (
    MlModelCreate,
    MlModelRead,
    ModelPredictionCreate,
    ModelPredictionRead,
)


def save_model(db: Session, data: MlModelCreate) -> MlModelRead:
    model = MlModel(**data.model_dump())
    db.add(model)
    try:
        db.commit()
        db.refresh(model)
    except Exception:
        db.rollback()
        raise
    return MlModelRead.model_validate(model)


def get_model(db: Session, model_id: str) -> MlModelRead | None:
    model = db.get(MlModel, model_id)
    return MlModelRead.model_validate(model) if model else None


def get_active_model(db: Session) -> MlModelRead | None:
    """The production model (newest first)."""
    model = (
        db.query(MlModel)
        .filter(MlModel.is_production.is_(True), MlModel.is_archived.is_(False))
        .order_by(MlModel.trained_at.desc())
        .first()
    )
    return MlModelRead.model_validate(model) if model else None


def archive_model(db: Session, model_id: str) -> bool:
    model = db.get(MlModel, model_id)
    if model is None:
        return False
    model.is_archived = True
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


def save_prediction(db: Session, data: ModelPredictionCreate) -> ModelPredictionRead:
    prediction = ModelPrediction(**data.model_dump())
    db.add(prediction)
    try:
        db.commit()
        db.refresh(prediction)
    except Exception:
        db.rollback()
        raise
    return ModelPredictionRead.model_validate(prediction)


def list_predictions_for_game(
    db: Session, game_id: str, model_id: str | None = None
) -> list[ModelPredictionRead]:
    query = db.query(ModelPrediction).filter(ModelPrediction.game_id == game_id)
    if model_id is not None:
        query = query.filter(ModelPrediction.model_id == model_id)
    rows = query.order_by(ModelPrediction.created_at.desc()).all()
    return [ModelPredictionRead.model_validate(r) for r in rows]
