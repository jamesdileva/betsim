"""Core Monte Carlo simulation: single-run trajectories and batch execution."""

from dataclasses import dataclass, field

import numpy as np

from simulation.bankroll import VALID_BET_SIZE_TYPES, calculate_stake
from simulation.odds import OddsConversion

__all__ = [
    "VALID_BET_SIZE_TYPES",
    "SimulationBatchResult",
    "calculate_stake",
    "simulate_batch",
    "simulate_once",
]


@dataclass
class SimulationBatchResult:
    """Aggregated output of one batch of simulations."""

    final_bankrolls: list[float]
    num_simulations: int
    num_bets: int
    seed: int | None
    trajectories: list[list[float]] = field(default_factory=list)


def validate_inputs(
    odds_decimal: float,
    win_probability: float,
    bankroll: float,
    bet_size: float,
    bet_size_type: str,
    num_bets: int,
) -> None:
    if odds_decimal < 1.0:
        raise ValueError(f"Decimal odds must be >= 1.0, got {odds_decimal}")
    if not 0.0 < win_probability < 1.0:
        raise ValueError(f"Win probability must be in (0, 1), got {win_probability}")
    if bankroll <= 0.0:
        raise ValueError(f"Bankroll must be positive, got {bankroll}")
    if bet_size <= 0.0:
        raise ValueError(f"Bet size must be positive, got {bet_size}")
    if bet_size_type not in VALID_BET_SIZE_TYPES:
        raise ValueError(f"bet_size_type must be one of {VALID_BET_SIZE_TYPES}")
    if num_bets < 1:
        raise ValueError(f"num_bets must be >= 1, got {num_bets}")


def simulate_once(
    odds_decimal: float,
    win_probability: float,
    bankroll: float,
    bet_size: float,
    bet_size_type: str,
    num_bets: int,
    rng: np.random.Generator,
) -> list[float]:
    """Run a single series of bets and return the full bankroll trajectory.

    Once the bankroll hits zero the run is ruined; the trajectory is padded
    with zeros so all trajectories in a batch share the same length.
    """
    validate_inputs(odds_decimal, win_probability, bankroll, bet_size, bet_size_type, num_bets)
    profit_multiplier = odds_decimal - 1.0

    trajectory = [bankroll]
    for _ in range(num_bets):
        if bankroll <= 0.0:
            trajectory.append(0.0)
            continue

        stake = calculate_stake(
            bankroll, bet_size, bet_size_type, odds_decimal, win_probability
        )
        if rng.random() < win_probability:
            bankroll += stake * profit_multiplier
        else:
            bankroll -= stake

        # Guard against float drift pushing the balance infinitesimally negative.
        bankroll = max(0.0, bankroll)
        trajectory.append(bankroll)

    return trajectory


def simulate_batch(
    odds_american: int | None = None,
    win_probability: float | None = None,
    bankroll: float | None = None,
    bet_size: float | None = None,
    bet_size_type: str = "flat",
    num_bets: int | None = None,
    num_simulations: int = 1000,
    seed: int | None = None,
    return_trajectories: bool = False,
    *,
    odds_decimal: float | None = None,
) -> SimulationBatchResult:
    """Run `num_simulations` independent simulations with a shared seeded RNG.

    Pass exactly one of odds_american / odds_decimal. Keyword-only params
    (odds_decimal) exist for derived bets such as parlays.
    """
    if num_simulations < 1:
        raise ValueError(f"num_simulations must be >= 1, got {num_simulations}")
    if (odds_american is None) == (odds_decimal is None):
        raise ValueError("Provide exactly one of odds_american / odds_decimal")
    if odds_decimal is None:
        assert odds_american is not None
        odds_decimal_value = OddsConversion.american_to_decimal(odds_american)
    else:
        odds_decimal_value = odds_decimal
    assert win_probability is not None and bankroll is not None and bet_size is not None
    assert num_bets is not None

    rng = np.random.default_rng(seed)

    final_bankrolls: list[float] = []
    trajectories: list[list[float]] = []

    for _ in range(num_simulations):
        traj = simulate_once(
            odds_decimal_value,
            win_probability,
            bankroll,
            bet_size,
            bet_size_type,
            num_bets,
            rng,
        )
        final_bankrolls.append(traj[-1])
        if return_trajectories:
            trajectories.append(traj)

    return SimulationBatchResult(
        final_bankrolls=final_bankrolls,
        num_simulations=num_simulations,
        num_bets=num_bets,
        seed=seed,
        trajectories=trajectories,
    )
