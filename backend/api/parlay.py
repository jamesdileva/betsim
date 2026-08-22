"""Parlay simulation endpoint: combined legs treated as a single bet."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.simulation import metric_summary
from crud.simulation import save_simulation_results, save_simulation_run
from schemas.api_simulation import DistributionData
from schemas.parlay import ParlayRequest, ParlayResponse
from schemas.simulation import SimulationResultCreate, SimulationRunCreate
from simulation.distribution import histogram
from simulation.metrics import calculate_metrics, max_drawdown
from simulation.monte_carlo import simulate_batch
from simulation.odds import OddsConversion

router = APIRouter()


@router.post("/parlay/simulate", response_model=ParlayResponse)
def simulate_parlay(request: ParlayRequest, db: Annotated[Session, Depends(get_db)]):
    decimals = [OddsConversion.american_to_decimal(leg.odds_american) for leg in request.legs]
    combined_probability = math.prod(leg.win_probability for leg in request.legs)
    combined_decimal = math.prod(decimals)
    ev_per_unit = combined_probability * (combined_decimal - 1.0) - (1.0 - combined_probability)
    break_even = 1.0 / combined_decimal

    batch = simulate_batch(
        win_probability=combined_probability,
        bankroll=request.bankroll,
        bet_size=request.bet_size,
        bet_size_type=request.bet_size_type,
        num_bets=request.num_bets,
        num_simulations=request.num_simulations,
        seed=request.seed,
        return_trajectories=True,
        odds_decimal=combined_decimal,
    )

    metrics = calculate_metrics(
        batch.final_bankrolls,
        batch.trajectories,
        starting_bankroll=request.bankroll,
    )
    edges, counts = histogram(batch.final_bankrolls)

    # Persist with the parlay's effective American odds for traceability.
    effective_american = OddsConversion.implied_prob_to_american(combined_probability)
    run = save_simulation_run(
        db,
        SimulationRunCreate(
            odds_american=effective_american,
            win_probability=combined_probability,
            bankroll=request.bankroll,
            bet_size=request.bet_size,
            bet_size_type=request.bet_size_type,
            num_bets=request.num_bets,
            num_simulations=request.num_simulations,
            seed=request.seed,
        ),
    )
    start = request.bankroll
    results = [
        SimulationResultCreate(
            run_index=i,
            final_bankroll=final,
            is_profitable=final > start,
            max_drawdown=max_drawdown(batch.trajectories[i]),
        )
        for i, final in enumerate(batch.final_bankrolls)
    ]
    save_simulation_results(db, run.id, results)

    return ParlayResponse(
        combined_probability=combined_probability,
        combined_decimal_odds=combined_decimal,
        ev_per_unit=ev_per_unit,
        break_even_probability=break_even,
        run_id=run.id,
        metrics=metric_summary(metrics),
        distribution=DistributionData(bin_edges=edges, counts=counts),
    )

