import pytest

from simulation.metrics import calculate_metrics, ev_per_bet, max_drawdown, risk_of_ruin
from simulation.monte_carlo import simulate_batch


class TestEvPerBet:
    def test_matches_theoretical_formula(self) -> None:
        # p=0.55 at -110 (decimal 1.9091), $10 stake:
        # 0.55 * 9.09 - 0.45 * 10 = 5.0 - 4.5 = +0.50
        ev = ev_per_bet(1.9090909, 0.55, 10.0)
        assert ev == pytest.approx(0.50, abs=1e-3)

    def test_negative_ev_no_edge(self) -> None:
        assert ev_per_bet(1.9090909, 0.50, 10.0) < 0

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(ValueError):
            ev_per_bet(0.5, 0.55, 10.0)
        with pytest.raises(ValueError):
            ev_per_bet(2.0, 1.5, 10.0)


class TestMaxDrawdown:
    def test_monotonic_growth_has_zero_drawdown(self) -> None:
        assert max_drawdown([100.0, 110.0, 120.0, 130.0]) == 0.0

    def test_simple_peak_trough(self) -> None:
        # peak 120 -> trough 70 = -50
        assert max_drawdown([100.0, 120.0, 70.0, 90.0]) == pytest.approx(-50.0)

    def test_later_deeper_trough_wins(self) -> None:
        # rises to 150, falls to 60: drawdown -90 beats the earlier -50
        assert max_drawdown([100.0, 150.0, 100.0, 60.0]) == pytest.approx(-90.0)

    def test_ruin_trajectory(self) -> None:
        assert max_drawdown([100.0, 50.0, 0.0, 0.0]) == pytest.approx(-100.0)


class TestRiskOfRuin:
    def test_fraction_of_busted_runs(self) -> None:
        assert risk_of_ruin([0.0, 500.0, 0.0, 1200.0]) == pytest.approx(0.5)

    def test_no_ruin(self) -> None:
        assert risk_of_ruin([100.0, 200.0]) == 0.0

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            risk_of_ruin([])


class TestCalculateMetrics:
    def _batch(self):
        return simulate_batch(
            odds_american=-110,
            win_probability=0.55,
            bankroll=1000.0,
            bet_size=5.0,
            bet_size_type="flat",
            num_bets=100,
            num_simulations=300,
            seed=42,
            return_trajectories=True,
        )

    def test_all_fields_present_and_sane(self) -> None:
        result = self._batch()
        metrics = calculate_metrics(result.final_bankrolls, result.trajectories)
        assert 0.0 <= metrics.win_pct <= 1.0
        assert 0.0 <= metrics.risk_of_ruin <= 1.0
        assert metrics.avg_ending_bankroll == pytest.approx(metrics.median_ending_bankroll, rel=0.5)
        assert metrics.worst_case_drawdown <= metrics.avg_max_drawdown <= 0.0
        assert metrics.min_bankroll >= 0.0

    def test_positive_edge_yields_positive_empirical_ev(self) -> None:
        result = self._batch()
        metrics = calculate_metrics(
            result.final_bankrolls,
            odds_american=-110,
            win_probability=0.55,
            num_bets=100,
            starting_bankroll=1000.0,
        )
        assert metrics.ev_per_bet > 0
        assert metrics.ev_total == pytest.approx(metrics.ev_per_bet * 100)

    def test_win_pct_counts_profitable_runs(self) -> None:
        finals = [1100.0, 900.0, 1000.0]
        metrics = calculate_metrics(finals, starting_bankroll=1000.0)
        assert metrics.win_pct == pytest.approx(1 / 3)

    def test_trajectory_bands(self) -> None:
        result = self._batch()
        metrics = calculate_metrics(
            result.final_bankrolls, result.trajectories, include_trajectory_bands=True
        )
        bands = metrics.trajectory_percentiles
        assert set(bands.keys()) == {"p10", "median", "p90", "min", "max"}
        n_points = 101  # start point + 100 bets
        for series in bands.values():
            assert len(series) == n_points
        # median starts at bankroll; min <= median <= max everywhere
        assert bands["median"][0] == pytest.approx(1000.0)
        assert all(
            lo <= md <= hi
            for lo, md, hi in zip(bands["min"], bands["median"], bands["max"], strict=True)
        )

    def test_bands_require_trajectories(self) -> None:
        with pytest.raises(ValueError):
            calculate_metrics([100.0], include_trajectory_bands=True)

    def test_empty_batch_raises(self) -> None:
        with pytest.raises(ValueError):
            calculate_metrics([])
