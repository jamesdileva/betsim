"""CRUD operations for simulation runs and their per-iteration results."""

from sqlalchemy.orm import Session, joinedload

from models import SimulationResult, SimulationRun
from schemas.simulation import (
    SimulationResultCreate,
    SimulationResultRead,
    SimulationRunCreate,
    SimulationRunRead,
)


def save_simulation_run(db: Session, data: SimulationRunCreate) -> SimulationRunRead:
    run = SimulationRun(**data.model_dump())
    db.add(run)
    try:
        db.commit()
        db.refresh(run)
    except Exception:
        db.rollback()
        raise
    return SimulationRunRead.model_validate(run)


def save_simulation_results(
    db: Session, simulation_run_id: int, results: list[SimulationResultCreate]
) -> int:
    """Bulk-insert per-simulation outcomes. Returns the number of rows added."""
    if not results:
        return 0
    rows = [
        SimulationResult(simulation_run_id=simulation_run_id, **r.model_dump())
        for r in results
    ]
    db.add_all(rows)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return len(rows)


def get_simulation_run(db: Session, run_id: int) -> SimulationRunRead | None:
    run = (
        db.query(SimulationRun)
        .options(joinedload(SimulationRun.results))
        .filter(SimulationRun.id == run_id)
        .first()
    )
    if not run:
        return None
    # touch the relationship so it loads before validation detaches the object
    _ = run.results
    return SimulationRunRead.model_validate(run)


def get_run_results(
    db: Session, run_id: int, limit: int | None = None
) -> list[SimulationResultRead]:
    query = (
        db.query(SimulationResult)
        .filter(SimulationResult.simulation_run_id == run_id)
        .order_by(SimulationResult.run_index)
    )
    if limit is not None:
        query = query.limit(limit)
    return [SimulationResultRead.model_validate(r) for r in query.all()]


def list_runs_for_strategy(db: Session, strategy_id: int) -> list[SimulationRunRead]:
    runs = (
        db.query(SimulationRun)
        .filter(SimulationRun.strategy_id == strategy_id)
        .order_by(SimulationRun.created_at.desc())
        .all()
    )
    return [SimulationRunRead.model_validate(r) for r in runs]


def list_run_summaries(db: Session, limit: int = 50) -> list[dict]:
    """Recent runs with aggregate stats from their stored results."""
    from sqlalchemy import case, func

    rows = (
        db.query(
            SimulationRun,
            func.count(SimulationResult.id),
            func.avg(SimulationResult.final_bankroll),
            func.sum(case((SimulationResult.is_profitable.is_(True), 1.0), else_=0.0)),
            func.sum(case((SimulationResult.final_bankroll <= 0.0, 1.0), else_=0.0)),
        )
        .outerjoin(
            SimulationResult,
            SimulationResult.simulation_run_id == SimulationRun.id,
        )
        .group_by(SimulationRun.id)
        .order_by(SimulationRun.created_at.desc(), SimulationRun.id.desc())
        .limit(limit)
        .all()
    )
    summaries = []
    for run, count, avg_final, profitable_sum, ruined_sum in rows:
        n = float(count) if count else 0.0
        summaries.append(
            {
                "run_id": run.id,
                "strategy_id": run.strategy_id,
                "odds_american": run.odds_american,
                "win_probability": run.win_probability,
                "bankroll": run.bankroll,
                "bet_size": run.bet_size,
                "bet_size_type": run.bet_size_type,
                "num_bets": run.num_bets,
                "num_simulations": run.num_simulations,
                "created_at": run.created_at,
                "result_count": int(count) if count else 0,
                "win_pct": (float(profitable_sum) / n) if n > 0 else None,
                "avg_final_bankroll": float(avg_final) if avg_final is not None else None,
                "risk_of_ruin": (float(ruined_sum) / n) if n > 0 else None,
            }
        )
    return summaries


def delete_simulation_run(db: Session, run_id: int) -> bool:
    run = db.get(SimulationRun, run_id)
    if run is None:
        return False
    db.query(SimulationResult).filter(
        SimulationResult.simulation_run_id == run_id
    ).delete(synchronize_session=False)
    db.delete(run)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
