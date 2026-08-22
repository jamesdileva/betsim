"""Bankroll strategy stake calculation: flat, percentage, Kelly, half-Kelly."""

from simulation.kelly import half_kelly, kelly_criterion

VALID_BET_SIZE_TYPES = ("flat", "percentage", "kelly", "half_kelly")


def calculate_stake(
    bankroll: float,
    bet_size: float,
    bet_size_type: str,
    odds_decimal: float,
    win_probability: float,
) -> float:
    """Stake for the current bet under the chosen strategy, capped at bankroll.

    bet_size semantics depend on the strategy:
      - flat: dollar amount per bet
      - percentage: fraction of current bankroll (e.g. 0.05 = 5%)
      - kelly / half_kelly: bet_size is ignored; fraction comes from Kelly
    """
    if bet_size_type == "flat":
        stake = bet_size
    elif bet_size_type == "percentage":
        stake = bankroll * bet_size
    elif bet_size_type == "kelly":
        stake = bankroll * kelly_criterion(odds_decimal, win_probability)
    elif bet_size_type == "half_kelly":
        stake = bankroll * half_kelly(odds_decimal, win_probability)
    else:
        raise ValueError(f"Unknown bet_size_type {bet_size_type!r}")
    return min(stake, bankroll)


def validate_bet_size(bet_size: float, bet_size_type: str) -> None:
    """Validate bet_size against its strategy's semantics.

    kelly / half_kelly derive the stake from the bankroll, so bet_size is
    ignored there and may be any non-negative value.
    """
    if not isinstance(bet_size_type, str) or bet_size_type not in VALID_BET_SIZE_TYPES:
        raise ValueError(f"bet_size_type must be one of {VALID_BET_SIZE_TYPES}")
    if bet_size < 0.0:
        raise ValueError(f"Bet size must be >= 0, got {bet_size}")
    if bet_size_type == "percentage" and bet_size > 1.0:
        raise ValueError(f"Percentage bet size must be <= 1.0 (100%), got {bet_size}")
