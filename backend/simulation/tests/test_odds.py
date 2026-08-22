import pytest

from simulation.odds import OddsConversion


class TestAmericanToDecimal:
    def test_negative_odds(self) -> None:
        assert OddsConversion.american_to_decimal(-110) == pytest.approx(1.9090909)
        assert OddsConversion.american_to_decimal(-150) == pytest.approx(1.6666667)

    def test_positive_odds(self) -> None:
        assert OddsConversion.american_to_decimal(150) == pytest.approx(2.5)
        assert OddsConversion.american_to_decimal(100) == pytest.approx(2.0)

    @pytest.mark.parametrize("bad", [0, -50, 99])
    def test_invalid_odds_raise(self, bad: int) -> None:
        with pytest.raises(ValueError):
            OddsConversion.american_to_decimal(bad)


class TestAmericanToImpliedProb:
    def test_negative_odds(self) -> None:
        assert OddsConversion.american_to_implied_prob(-110) == pytest.approx(0.5238095)

    def test_positive_odds(self) -> None:
        assert OddsConversion.american_to_implied_prob(150) == pytest.approx(0.40)

    @pytest.mark.parametrize("bad", [0, -50, 99])
    def test_invalid_odds_raise(self, bad: int) -> None:
        with pytest.raises(ValueError):
            OddsConversion.american_to_implied_prob(bad)


class TestRoundTrips:
    @pytest.mark.parametrize("odds", [-400, -200, -110, 100, 150, 300])
    def test_american_decimal_prob_round_trip(self, odds: int) -> None:
        decimal = OddsConversion.american_to_decimal(odds)
        prob = OddsConversion.decimal_to_implied_prob(decimal)
        assert OddsConversion.implied_prob_to_american(prob) == odds

    def test_edge(self) -> None:
        # 55% win prob at decimal 1.9091 -> +5% edge per unit staked
        edge = OddsConversion.edge(OddsConversion.american_to_decimal(-110), 0.55)
        assert edge == pytest.approx(0.05, abs=1e-4)

    def test_edge_negative_when_no_value(self) -> None:
        edge = OddsConversion.edge(OddsConversion.american_to_decimal(-110), 0.50)
        assert edge < 0
