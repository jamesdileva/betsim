"""Portfolio endpoints: build today's portfolio and browse history."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.portfolios import get_portfolio_items
from ml.portfolio import build_portfolio, score_predictions
from models import Game, ModelPrediction
from schemas.portfolio import PortfolioRead

router = APIRouter()


@router.post("/portfolio/build", response_model=PortfolioRead)
def build(
    db: Annotated[Session, Depends(get_db)],
    bankroll: Annotated[float, Query(gt=0.0)] = 1000.0,
    model_id: Annotated[str | None, Query(max_length=100)] = None,
):
    """Score all scheduled-game predictions and construct a portfolio."""
    if model_id is not None:
        from crud.ml_models import get_model

        if get_model(db, model_id) is None:
            raise HTTPException(status_code=404, detail="Model not found")
    saved, _scored = build_portfolio(db, bankroll=bankroll, model_id=model_id)
    return saved


@router.get("/portfolio/latest", response_model=PortfolioRead | None)
def latest(db: Annotated[Session, Depends(get_db)]):
    from models import Portfolio

    portfolio = (
        db.query(Portfolio).order_by(Portfolio.id.desc()).first()
    )
    return PortfolioRead.model_validate(portfolio) if portfolio else None


@router.get("/portfolio/history")
def history(db: Annotated[Session, Depends(get_db)]) -> dict:
    from models import Portfolio

    portfolios = (
        db.query(Portfolio).order_by(Portfolio.id.desc()).limit(50).all()
    )
    return {
        "portfolios": [
            {
                "id": p.id,
                "date": p.date.isoformat() if p.date else None,
                "total_risk": p.total_risk,
                "expected_roi": p.expected_roi,
                "kelly_exposure": p.kelly_exposure,
                "items": len(get_portfolio_items(db, p.id)),
            }
            for p in portfolios
        ]
    }


@router.get("/portfolio/scored")
def scored_preview(db: Annotated[Session, Depends(get_db)]) -> dict:
    """Scored predictions without building/persisting a portfolio."""
    predictions = (
        db.query(ModelPrediction, Game)
        .outerjoin(Game, ModelPrediction.game_id == Game.id)
        .filter(Game.status.is_(None) | (Game.status != "final"))
        .limit(100)
        .all()
    )
    scored = score_predictions(db, list(predictions))
    return {
        "predictions": [
            {
                "model_id": s.prediction.model_id,
                "game_id": s.prediction.game_id,
                "predicted_probability": s.prediction.predicted_probability,
                "score": s.score.score,
                "stars": s.score.stars,
                "risk_level": s.score.risk_level,
                "band": _band(s.score.score),
            }
            for s in scored
        ]
    }


def _band(score: int) -> str | None:
    from ml.portfolio import BAND_RULES

    for band, rules in BAND_RULES.items():
        if score >= rules["min_score"]:
            return band
    return None
