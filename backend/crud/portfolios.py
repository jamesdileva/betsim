"""CRUD operations for portfolios and their items."""

from sqlalchemy.orm import Session

from models import ModelEvaluation, Portfolio, PortfolioItem
from schemas.portfolio import (
    ModelEvaluationCreate,
    ModelEvaluationRead,
    PortfolioCreate,
    PortfolioItemRead,
    PortfolioRead,
)


def save_portfolio(db: Session, data: PortfolioCreate) -> PortfolioRead:
    items = data.items
    portfolio = Portfolio(**data.model_dump(exclude={"items"}))
    db.add(portfolio)
    try:
        db.flush()  # assign portfolio.id before inserting items
        for item in items:
            db.add(PortfolioItem(portfolio_id=portfolio.id, **item.model_dump()))
        db.commit()
        db.refresh(portfolio)
    except Exception:
        db.rollback()
        raise
    return PortfolioRead.model_validate(portfolio)


def get_portfolio(db: Session, portfolio_id: int) -> PortfolioRead | None:
    portfolio = db.get(Portfolio, portfolio_id)
    return PortfolioRead.model_validate(portfolio) if portfolio else None


def get_portfolio_items(
    db: Session, portfolio_id: int
) -> list[PortfolioItemRead]:
    rows = (
        db.query(PortfolioItem)
        .filter(PortfolioItem.portfolio_id == portfolio_id)
        .order_by(PortfolioItem.id)
        .all()
    )
    return [PortfolioItemRead.model_validate(r) for r in rows]


def save_model_evaluation(
    db: Session, data: ModelEvaluationCreate
) -> ModelEvaluationRead:
    row = ModelEvaluation(**data.model_dump())
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except Exception:
        db.rollback()
        raise
    return ModelEvaluationRead.model_validate(row)


def list_evaluations_for_model(
    db: Session, model_id: str
) -> list[ModelEvaluationRead]:
    rows = (
        db.query(ModelEvaluation)
        .filter(ModelEvaluation.model_id == model_id)
        .order_by(ModelEvaluation.evaluated_at.desc())
        .all()
    )
    return [ModelEvaluationRead.model_validate(r) for r in rows]
