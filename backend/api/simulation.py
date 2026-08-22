"""Simulation endpoints: run Monte Carlo batches, persist and return results."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.simulation import save_simulation_results, save_simulation_run
from crud.strategy import get_strategy
from schemas.api_simulation import (
    DistributionData,
    MetricSummary,
    SimulationRequest,
    SimulationResponse,
    TrajectoryBands,
)
from schemas.simulation import SimulationResultCreate, SimulationRunCreate
from schemas.strategy import StrategyUpdate
from simulation.distribution import histogram, percentile_bands
from simulation.metrics import Metrics, calculate_metrics, max_drawdown
from simulation.monte_carlo import simulate_batch

router = APIRouter()


def metric_summary(metrics: Metrics) -> MetricSummary:
    data = {k: v for k, v in asdict(metrics).items() if k != "trajectory_percentiles"}
    return MetricSummary(**data)


def _run_and_respond(
    db: Session,
    request: SimulationRequest,
    strategy_id: int | None = None,
) -> SimulationResponse:
    result = simulate_batch(
        odds_american=request.odds_american,
        win_probability=request.win_probability,
        bankroll=request.bankroll,
        bet_size=request.bet_size,
        bet_size_type=request.bet_size_type,
        num_bets=request.num_bets,
        num_simulations=request.num_simulations,
        seed=request.seed,
        return_trajectories=True,
    )

    metrics = calculate_metrics(
        result.final_bankrolls,
        result.trajectories,
        starting_bankroll=request.bankroll,
        odds_american=request.odds_american,
        win_probability=request.win_probability,
        num_bets=request.num_bets,
        include_trajectory_bands=True,
    )
    edges, counts = histogram(result.final_bankrolls)

    run_create = SimulationRunCreate(**request.model_dump(), strategy_id=strategy_id)
    run = save_simulation_run(db, run_create)

    start = request.bankroll
    results = [
        SimulationResultCreate(
            run_index=i,
            final_bankroll=final,
            is_profitable=final > start,
            max_drawdown=max_drawdown(result.trajectories[i]),
        )
        for i, final in enumerate(result.final_bankrolls)
    ]
    save_simulation_results(db, run.id, results)

    bands = percentile_bands(result.trajectories)
    return SimulationResponse(
        run_id=run.id,
        metrics=metric_summary(metrics),
        distribution=DistributionData(bin_edges=edges, counts=counts),
        trajectory=TrajectoryBands(**bands),
        created_at=run.created_at,
    )


@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest, db: Annotated[Session, Depends(get_db)]):
    return _run_and_respond(db, request)


@router.post("/simulate/{strategy_id}", response_model=SimulationResponse)
def run_strategy_simulation(
    strategy_id: int,
    db: Annotated[Session, Depends(get_db)],
    overrides: StrategyUpdate | None = None,
):
    """Run a simulation from a saved strategy; body may override sim params."""
    strategy = get_strategy(db, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")

    params = {
        "odds_american": strategy.odds_american,
        "win_probability": strategy.win_probability,
        "bankroll": strategy.bankroll,
        "bet_size": strategy.bet_size,
        "bet_size_type": strategy.bet_size_type or "flat",
        "num_bets": strategy.num_bets or 100,
        "num_simulations": strategy.num_simulations or 5000,
    }
    if overrides is not None:
        allowed = {"num_simulations", "num_bets", "seed"}
        override_data = overrides.model_dump(exclude_unset=True)
        params.update({k: v for k, v in override_data.items() if k in allowed})
        if overrides.bet_size_type is not None:
            params["bet_size_type"] = overrides.bet_size_type
        if overrides.bet_size is not None:
            params["bet_size"] = overrides.bet_size

    try:
        request = SimulationRequest(**params)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _run_and_respond(db, request, strategy_id=strategy_id)

