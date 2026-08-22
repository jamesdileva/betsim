"""Odds conversion utilities: American <-> Decimal <-> Implied Probability."""


class OddsConversion:
    """Static converters between American odds, decimal odds, and implied probability.

    Note: the Tech Spec's American->Decimal formula contains a typo; the
    correct formulas are implemented here and covered by tests.
    """

    @staticmethod
    def validate_american(odds_american: int) -> None:
        if odds_american == 0 or abs(odds_american) < 100:
            raise ValueError(
                f"Invalid American odds {odds_american}: must be a nonzero value "
                "with magnitude >= 100 (e.g. -110, +150)."
            )

    @staticmethod
    def american_to_decimal(odds_american: int) -> float:
        OddsConversion.validate_american(odds_american)
        if odds_american > 0:
            return 1.0 + odds_american / 100.0
        return 1.0 + 100.0 / abs(odds_american)

    @staticmethod
    def american_to_implied_prob(odds_american: int) -> float:
        OddsConversion.validate_american(odds_american)
        if odds_american > 0:
            return 100.0 / (odds_american + 100.0)
        return float(abs(odds_american)) / (abs(odds_american) + 100.0)

    @staticmethod
    def decimal_to_implied_prob(decimal_odds: float) -> float:
        if decimal_odds < 1.0:
            raise ValueError(f"Decimal odds must be >= 1.0, got {decimal_odds}")
        return 1.0 / decimal_odds

    @staticmethod
    def implied_prob_to_decimal(implied_prob: float) -> float:
        if not 0.0 < implied_prob <= 1.0:
            raise ValueError(f"Implied probability must be in (0, 1], got {implied_prob}")
        return 1.0 / implied_prob

    @staticmethod
    def implied_prob_to_american(implied_prob: float) -> int:
        if not 0.0 < implied_prob < 1.0:
            raise ValueError(f"Implied probability must be in (0, 1), got {implied_prob}")
        if implied_prob <= 0.5:
            return round(100.0 * (1.0 - implied_prob) / implied_prob)
        return round(-100.0 * implied_prob / (1.0 - implied_prob))

    @staticmethod
    def edge(decimal_odds: float, win_probability: float) -> float:
        """Expected return per unit staked: p * decimal - 1. Positive = +EV."""
        return win_probability * decimal_odds - 1.0
