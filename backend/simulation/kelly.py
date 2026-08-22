"""Kelly Criterion stake-fraction calculations."""


def kelly_criterion(odds_decimal: float, win_probability: float) -> float:
    """Optimal fraction of bankroll to bet: (b*p - q) / b where b = decimal - 1.

    Returns 0.0 when there is no edge (negative Kelly) or inputs are degenerate;
    result is clamped to [0, 1].
    """
    b = odds_decimal - 1.0
    p = win_probability
    q = 1.0 - win_probability
    if b <= 0.0 or not 0.0 < p < 1.0:
        return 0.0
    fraction = (b * p - q) / b
    return max(0.0, min(1.0, fraction))


def half_kelly(odds_decimal: float, win_probability: float) -> float:
    """Half-Kelly fraction — same expected log growth at reduced variance."""
    return kelly_criterion(odds_decimal, win_probability) / 2.0
