"""Analytics endpoints: run backtests and inspect model performance."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.ml_models import get_model
from ml.backtest import run_backtest

router = APIRouter()


@router.post("/analytics/run-backtests")
def trigger_backtests(
    db: Annotated[Session, Depends(get_db)],
    model_id: Annotated[str | None, Query(max_length=100)] = None,
) -> dict[str, Any]:
    """Replay finished games' predictions into backtest results."""
    if model_id is not None and get_model(db, model_id) is None:
        raise HTTPException(status_code=404, detail="Model not found")
    created = run_backtest(db, model_id=model_id)
    return {"backtests_created": created}


@router.get("/analytics/performance")
def performance(
    db: Annotated[Session, Depends(get_db)],
    model_id: Annotated[str | None, Query(max_length=100)] = None,
) -> dict[str, Any]:
    """Latest evaluation + full evaluation history per model (or all models)."""
    from models import BacktestResult, ModelEvaluation

    eval_query = db.query(ModelEvaluation)
    if model_id is not None:
        if get_model(db, model_id) is None:
            raise HTTPException(status_code=404, detail="Model not found")
        eval_query = eval_query.filter(ModelEvaluation.model_id == model_id)

    evaluations: dict[str, list[dict[str, Any]]] = {}
    for row in eval_query.order_by(ModelEvaluation.evaluated_at.desc()).all():
        evaluations.setdefault(row.model_id, []).append(
            {
                "id": row.id,
                "evaluated_at": row.evaluated_at.isoformat() if row.evaluated_at else None,
                "accuracy": row.accuracy,
                "calibration_error": row.calibration_error,
                "avg_roi": row.avg_roi,
                "brier_score": row.brier_score,
                "notes": row.notes,
            }
        )

    bt_query = db.query(
        BacktestResult.model_id,
        BacktestResult.predicted_probability,
        BacktestResult.actual_outcome,
        BacktestResult.roi,
    )
    if model_id is not None:
        bt_query = bt_query.filter(BacktestResult.model_id == model_id)
    rows = bt_query.all()

    totals: dict[str, dict[str, float | int]] = {}
    for model, p, outcome, roi in rows:
        bucket = totals.setdefault(model, {"count": 0, "correct": 0, "roi_sum": 0.0, "roi_n": 0})
        if outcome is None or p is None:
            continue
        bucket["count"] += 1
        bucket["correct"] += 1 if (p >= 0.5) == bool(outcome) else 0
        if roi is not None:
            bucket["roi_sum"] += float(roi)
            bucket["roi_n"] += 1

    summary = [
        {
            "model_id": m,
            "backtest_count": b["count"],
            "accuracy": round(b["correct"] / b["count"], 4) if b["count"] else None,
            "avg_roi": round(b["roi_sum"] / b["roi_n"], 6) if b["roi_n"] else None,
        }
        for m, b in sorted(totals.items())
    ]

    return {"summary": summary, "evaluations": evaluations}


@router.get("/analytics/portfolio-history")
def portfolio_history(db: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    """Stored portfolios (populated from Sprint 14 onward)."""
    from crud.portfolios import get_portfolio_items
    from models import Portfolio

    portfolios = (
        db.query(Portfolio).order_by(Portfolio.date.desc(), Portfolio.id.desc()).limit(50).all()
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


