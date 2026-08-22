import pytest

from simulation.bankroll import calculate_stake, validate_bet_size


class TestCalculateStake:
    def test_flat(self) -> None:
        assert calculate_stake(1000, 50, "flat", 1.9091, 0.55) == 50.0

    def test_percentage(self) -> None:
        assert calculate_stake(1000, 0.05, "percentage", 1.9091, 0.55) == pytest.approx(50.0)

    def test_kelly_uses_fraction_of_current_bankroll(self) -> None:
        stake = calculate_stake(2000, 50, "kelly", 1.9091, 0.55)
        assert stake == pytest.approx(2000 * 0.055, abs=0.5)

    def test_half_kelly(self) -> None:
        stake = calculate_stake(2000, 50, "half_kelly", 1.9091, 0.55)
        assert stake == pytest.approx(2000 * 0.055 / 2, abs=0.5)

    def test_stake_capped_at_bankroll(self) -> None:
        assert calculate_stake(10, 500, "flat", 1.9091, 0.55) == 10.0

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError):
            calculate_stake(1000, 50, "martingale", 1.9091, 0.55)


class TestValidateBetSize:
    @pytest.mark.parametrize(
        ("bet_size", "bet_size_type"),
        [(50, "flat"), (0.05, "percentage"), (0, "kelly")],
    )
    def test_accepts_valid(self, bet_size: float, bet_size_type: str) -> None:
        validate_bet_size(bet_size, bet_size_type)

    def test_rejects_negative(self) -> None:
        with pytest.raises(ValueError):
            validate_bet_size(-5.0, "flat")

    def test_rejects_percentage_over_100pct(self) -> None:
        with pytest.raises(ValueError):
            validate_bet_size(1.5, "percentage")

    def test_allows_any_positive_dollar_for_kelly(self) -> None:
        validate_bet_size(12345.0, "kelly")
