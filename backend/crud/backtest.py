"""CRUD operations for backtest results."""

from sqlalchemy.orm import Session

from models import BacktestResult
from schemas.portfolio import BacktestResultCreate, BacktestResultRead


def save_backtest_result(db: Session, data: BacktestResultCreate) -> BacktestResultRead:
    row = BacktestResult(**data.model_dump())
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except Exception:
        db.rollback()
        raise
    return BacktestResultRead.model_validate(row)


def save_backtest_results(
    db: Session, results: list[BacktestResultCreate]
) -> int:
    """Bulk-insert backtest rows (e.g. a full replay). Returns count added."""
    if not results:
        return 0
    rows = [BacktestResult(**r.model_dump()) for r in results]
    db.add_all(rows)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return len(rows)


def get_model_backtests(
    db: Session, model_id: str, limit: int | None = None
) -> list[BacktestResultRead]:
    query = (
        db.query(BacktestResult)
        .filter(BacktestResult.model_id == model_id)
        .order_by(BacktestResult.created_at.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    return [BacktestResultRead.model_validate(r) for r in query.all()]
