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
