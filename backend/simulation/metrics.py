"""Aggregated metrics computed from a batch of simulated trajectories."""

from dataclasses import dataclass, field

import numpy as np

from simulation.distribution import percentile_bands


@dataclass
class Metrics:
    """Summary statistics across all simulations in a batch."""

    win_pct: float
    avg_ending_bankroll: float
    median_ending_bankroll: float
    std_dev: float
    min_bankroll: float
    max_bankroll: float
    risk_of_ruin: float
    avg_max_drawdown: float
    worst_case_drawdown: float
    ev_per_bet: float
    ev_total: float
    trajectory_percentiles: dict[str, list[float]] = field(default_factory=dict)


def ev_per_bet(odds_decimal: float, win_probability: float, stake: float) -> float:
    """Theoretical expected value of one bet: p * profit - q * stake."""
    if odds_decimal < 1.0:
        raise ValueError(f"Decimal odds must be >= 1.0, got {odds_decimal}")
    if not 0.0 <= win_probability <= 1.0:
        raise ValueError(f"Win probability must be in [0, 1], got {win_probability}")
    profit = stake * (odds_decimal - 1.0)
    return win_probability * profit - (1.0 - win_probability) * stake


def max_drawdown(trajectory: list[float]) -> float:
    """Worst peak-to-trough decline within one trajectory.

    Returned as a negative dollar amount (0.0 if the bankroll never declines).
    """
    peak = trajectory[0] if trajectory else 0.0
    worst = 0.0
    for value in trajectory:
        if value > peak:
            peak = value
        drawdown = value - peak
        if drawdown < worst:
            worst = drawdown
    return worst


def risk_of_ruin(final_bankrolls: list[float]) -> float:
    """Fraction of simulations where the bankroll hit zero."""
    if not final_bankrolls:
        raise ValueError("final_bankrolls must not be empty")
    return sum(1.0 for f in final_bankrolls if f <= 0.0) / len(final_bankrolls)


def calculate_metrics(
    final_bankrolls: list[float],
    trajectories: list[list[float]] | None = None,
    starting_bankroll: float | None = None,
    odds_american: int | None = None,
    win_probability: float | None = None,
    num_bets: int | None = None,
    include_trajectory_bands: bool = False,
) -> Metrics:
    """Aggregate metrics over a batch of simulations.

    EV is empirical: (mean final bankroll - start) / num_bets, which is exact
    in expectation for any staking strategy and matches the theoretical flat
    formula asymptotically. Trajectory bands require rectangular trajectories
    (simulate_batch guarantees this via ruin padding).
    """
    if not final_bankrolls:
        raise ValueError("final_bankrolls must not be empty")

    final = np.asarray(final_bankrolls, dtype=float)
    start = (
        starting_bankroll
        if starting_bankroll is not None
        else (trajectories[0][0] if trajectories else final[0])
    )

    drawdowns = (
        [max_drawdown(traj) for traj in trajectories]
        if trajectories
        else []
    )
    avg_drawdown = float(np.mean(drawdowns)) if drawdowns else 0.0
    worst_drawdown = float(np.min(drawdowns)) if drawdowns else 0.0

    ev_per_bet_value = 0.0
    if odds_american is not None and win_probability is not None and num_bets:
        ev_per_bet_value = (float(np.mean(final)) - start) / num_bets

    bands: dict[str, list[float]] = {}
    if include_trajectory_bands:
        if not trajectories:
            raise ValueError("include_trajectory_bands requires trajectories")
        bands = percentile_bands(trajectories)

    return Metrics(
        win_pct=float(np.mean(final > start)),
        avg_ending_bankroll=float(np.mean(final)),
        median_ending_bankroll=float(np.median(final)),
        std_dev=float(np.std(final)),
        min_bankroll=float(np.min(final)),
        max_bankroll=float(np.max(final)),
        risk_of_ruin=risk_of_ruin(final_bankrolls),
        avg_max_drawdown=avg_drawdown,
        worst_case_drawdown=worst_drawdown,
        ev_per_bet=ev_per_bet_value,
        ev_total=ev_per_bet_value * (num_bets or 0),
        trajectory_percentiles=bands,
    )
