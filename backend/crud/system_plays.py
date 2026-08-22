"""CRUD operations for System Plays calibration results."""

from sqlalchemy.orm import Session

from models import SystemPlayResult
from schemas.ml_model import SystemPlayResultCreate, SystemPlayResultRead


def save_calibration_result(
    db: Session, data: SystemPlayResultCreate
) -> SystemPlayResultRead:
    row = SystemPlayResult(**data.model_dump())
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except Exception:
        db.rollback()
        raise
    return SystemPlayResultRead.model_validate(row)


def list_calibration_results(
    db: Session, limit: int | None = None
) -> list[SystemPlayResultRead]:
    query = db.query(SystemPlayResult).order_by(SystemPlayResult.created_at.desc())
    if limit is not None:
        query = query.limit(limit)
    return [SystemPlayResultRead.model_validate(r) for r in query.all()]
