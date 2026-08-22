import time

import numpy as np
import pytest

from simulation.monte_carlo import (
    SimulationBatchResult,
    simulate_batch,
    simulate_once,
)


class TestSimulateOnce:
    def _run(self, rng: np.random.Generator, **overrides):
        params = {
            "odds_decimal": 2.0,
            "win_probability": 0.5,
            "bankroll": 100.0,
            "bet_size": 10.0,
            "bet_size_type": "flat",
            "num_bets": 3,
            "rng": rng,
        }
        params.update(overrides)
        return simulate_once(**params)

    def test_trajectory_length_and_start(self, rng: np.random.Generator) -> None:
        traj = self._run(rng)
        assert len(traj) == 4
        assert traj[0] == 100.0

    def test_deterministic_with_same_seed(self) -> None:
        kwargs = dict(
            odds_decimal=1.9090909,
            win_probability=0.55,
            bankroll=1000.0,
            bet_size=50.0,
            bet_size_type="flat",
            num_bets=50,
        )
        a = simulate_once(rng=np.random.default_rng(7), **kwargs)
        b = simulate_once(rng=np.random.default_rng(7), **kwargs)
        assert a == b

    def test_known_sequence_flat_betting(self, rng: np.random.Generator) -> None:
        # decimal 2.0: each win adds exactly the stake, each loss subtracts it.
        # Replay the rng to compute the expectation independently.
        draws = [rng.random() < 0.5 for _ in range(3)]
        expected = [100.0]
        for won in draws:
            expected.append(expected[-1] + (10.0 if won else -10.0))
        actual = self._run(np.random.default_rng(42))
        assert actual == expected

    def test_ruin_pads_trajectory_with_zeros(self) -> None:
        # $10 bankroll, $10 flat bets at even money: first loss = ruin.
        rng = np.random.default_rng(0)  # first draw < 0.5 -> loss
        traj = simulate_once(
            odds_decimal=2.0,
            win_probability=0.5,
            bankroll=10.0,
            bet_size=10.0,
            bet_size_type="flat",
            num_bets=5,
            rng=rng,
        )
        assert traj[0] == 10.0
        assert all(v == 0.0 for v in traj[-4:])
        assert len(traj) == 6

    @pytest.mark.parametrize("bad", [-1.0, 0.0])
    def test_invalid_bankroll_raises(self, bad: float, rng: np.random.Generator) -> None:
        with pytest.raises(ValueError):
            self._run(rng, bankroll=bad)

    def test_invalid_win_prob_raises(self, rng: np.random.Generator) -> None:
        with pytest.raises(ValueError):
            self._run(rng, win_probability=1.0)

    def test_invalid_num_bets_raises(self, rng: np.random.Generator) -> None:
        with pytest.raises(ValueError):
            self._run(rng, num_bets=0)


class TestSimulateBatch:
    def test_returns_result_shape(self) -> None:
        result = simulate_batch(-110, 0.55, 1000.0, 5.0, "flat", 100, num_simulations=10, seed=1)
        assert isinstance(result, SimulationBatchResult)
        assert len(result.final_bankrolls) == 10
        assert result.num_simulations == 10
        assert result.seed == 1

    def test_deterministic_with_same_seed(self) -> None:
        kwargs = dict(odds_american=-110, win_probability=0.55, bankroll=1000.0,
                      bet_size=5.0, bet_size_type="flat", num_bets=20,
                      num_simulations=25)
        a = simulate_batch(seed=99, **kwargs)
        b = simulate_batch(seed=99, **kwargs)
        assert a.final_bankrolls == b.final_bankrolls

    def test_positive_edge_grows_bankroll_on_average(self) -> None:
        # +5% edge per unit staked over 100 bets must trend upward.
        result = simulate_batch(-110, 0.55, 1000.0, 5.0, "flat", 100, seed=42)
        assert sum(result.final_bankrolls) / len(result.final_bankrolls) > 1000.0

    def test_win_rate_tracks_true_probability(self) -> None:
        # With tiny flat stakes, fraction of profitable runs should be well
        # above 50% but individual-bet frequency tracks p; use single-bet sims.
        result = simulate_batch(-110, 0.55, 100.0, 1.0, "flat", 1, num_simulations=4000, seed=7)
        wins = sum(f > 100.0 for f in result.final_bankrolls)
        assert wins / len(result.final_bankrolls) == pytest.approx(0.55, abs=0.03)

    def test_ruin_occurs_with_aggressive_sizing_and_no_edge(self) -> None:
        # All-in style betting at -EV ruins most runs.
        result = simulate_batch(-110, 0.45, 100.0, 90.0, "flat", 50, seed=3)
        ruined = sum(f <= 0.0 for f in result.final_bankrolls)
        assert ruined > len(result.final_bankrolls) * 0.8

    def test_trajectories_optional(self) -> None:
        without = simulate_batch(-110, 0.55, 1000.0, 5.0, "flat", 10, num_simulations=3, seed=1)
        assert without.trajectories == []
        with_trajs = simulate_batch(
            -110, 0.55, 1000.0, 5.0, "flat", 10, num_simulations=3, seed=1,
            return_trajectories=True,
        )
        assert len(with_trajs.trajectories) == 3
        assert all(len(t) == 11 for t in with_trajs.trajectories)

    def test_performance_target(self) -> None:
        start = time.perf_counter()
        simulate_batch(-110, 0.55, 1000.0, 50.0, "flat", 100, num_simulations=1000, seed=42)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.5, f"1000x100 took {elapsed:.3f}s (target < 0.5s)"
