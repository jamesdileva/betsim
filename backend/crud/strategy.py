"""CRUD operations for the strategies table."""

from sqlalchemy.orm import Session

from models import Strategy
from schemas.strategy import StrategyCreate, StrategyRead, StrategyUpdate


def _commit(db: Session) -> None:
    db.commit()


def save_strategy(db: Session, data: StrategyCreate) -> StrategyRead:
    strategy = Strategy(**data.model_dump())
    db.add(strategy)
    try:
        _commit(db)
        db.refresh(strategy)
    except Exception:
        db.rollback()
        raise
    return StrategyRead.model_validate(strategy)


def get_strategy(db: Session, strategy_id: int) -> StrategyRead | None:
    strategy = db.get(Strategy, strategy_id)
    return StrategyRead.model_validate(strategy) if strategy else None


def list_strategies(db: Session) -> list[StrategyRead]:
    rows = (
        db.query(Strategy)
        .order_by(Strategy.created_at.desc(), Strategy.id.desc())
        .all()
    )
    return [StrategyRead.model_validate(r) for r in rows]


def update_strategy(
    db: Session, strategy_id: int, data: StrategyUpdate
) -> StrategyRead | None:
    strategy = db.get(Strategy, strategy_id)
    if strategy is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(strategy, key, value)
    try:
        _commit(db)
        db.refresh(strategy)
    except Exception:
        db.rollback()
        raise
    return StrategyRead.model_validate(strategy)


def delete_strategy(db: Session, strategy_id: int) -> bool:
    strategy = db.get(Strategy, strategy_id)
    if strategy is None:
        return False
    db.delete(strategy)
    try:
        _commit(db)
    except Exception:
        db.rollback()
        raise
    return True
