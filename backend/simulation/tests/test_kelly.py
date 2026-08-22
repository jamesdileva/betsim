import pytest

from simulation.kelly import half_kelly, kelly_criterion


class TestKellyCriterion:
    def test_formula_matches_bp_minus_q_over_b(self) -> None:
        # b = 1.9091 - 1, p = 0.55 -> (b*p - q)/b ~= 0.055
        assert kelly_criterion(1.9090909, 0.55) == pytest.approx(0.055, abs=1e-4)

    def test_even_money_with_edge(self) -> None:
        # decimal 2.0 (b=1), p=0.6 -> (0.6 - 0.4)/1 = 0.2
        assert kelly_criterion(2.0, 0.60) == pytest.approx(0.20)

    def test_no_edge_returns_zero(self) -> None:
        # 50% at -110 is -EV; Kelly must not recommend betting
        assert kelly_criterion(1.9090909, 0.50) == 0.0

    def test_degenerate_inputs_return_zero(self) -> None:
        assert kelly_criterion(1.0, 0.6) == 0.0  # no profit possible
        assert kelly_criterion(2.0, 0.0) == 0.0
        assert kelly_criterion(2.0, 1.0) == 0.0

    def test_half_kelly_is_half(self) -> None:
        full = kelly_criterion(1.9090909, 0.55)
        assert half_kelly(1.9090909, 0.55) == pytest.approx(full / 2)
