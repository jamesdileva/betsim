import pytest


def test_health(client) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/health").json() == {"status": "ok"}


class TestSimulate:
    def _payload(self, **overrides):
        base = {
            "odds_american": -110,
            "win_probability": 0.55,
            "bankroll": 1000.0,
            "bet_size": 5.0,
            "bet_size_type": "flat",
            "num_bets": 20,
            "num_simulations": 500,
            "seed": 42,
        }
        base.update(overrides)
        return base

    def test_run_simulation_returns_full_payload(self, client) -> None:
        response = client.post("/api/simulate", json=self._payload())
        assert response.status_code == 200
        body = response.json()

        assert body["run_id"] > 0
        metrics = body["metrics"]
        assert 0.0 <= metrics["win_pct"] <= 1.0
        assert 0.0 <= metrics["risk_of_ruin"] <= 1.0
        assert metrics["ev_per_bet"] > 0  # +edge input

        dist = body["distribution"]
        assert len(dist["bin_edges"]) == len(dist["counts"]) + 1
        assert sum(dist["counts"]) == self._payload()["num_simulations"]

        traj = body["trajectory"]
        assert set(traj.keys()) == {"p10", "median", "p90", "min", "max"}
        assert len(traj["median"]) == self._payload()["num_bets"] + 1
        assert traj["median"][0] == pytest.approx(1000.0)

    def test_deterministic_with_seed(self, client) -> None:
        a = client.post("/api/simulate", json=self._payload()).json()
        b = client.post("/api/simulate", json=self._payload()).json()
        assert a["metrics"]["avg_ending_bankroll"] == pytest.approx(
            b["metrics"]["avg_ending_bankroll"]
        )

    def test_invalid_odds_return_422(self, client) -> None:
        response = client.post("/api/simulate", json=self._payload(odds_american=-50))
        assert response.status_code == 422

    def test_invalid_probability_returns_422(self, client) -> None:
        response = client.post("/api/simulate", json=self._payload(win_probability=1.5))
        assert response.status_code == 422

    def test_persists_results(self, client) -> None:
        first = client.post("/api/simulate", json=self._payload()).json()
        second = client.post("/api/simulate", json=self._payload()).json()
        assert second["run_id"] > first["run_id"]


class TestStrategyEndpointsAndSimulation:
    def _strategy(self) -> dict:
        return {
            "name": "NFL Week 1",
            "odds_american": -110,
            "win_probability": 0.55,
            "bankroll": 1000.0,
            "bet_size": 50.0,
            "bet_size_type": "flat",
            "num_bets": 100,
            "num_simulations": 500,
        }

    def test_crud_cycle(self, client) -> None:
        created = client.post("/api/strategies", json=self._strategy())
        assert created.status_code == 201
        strategy_id = created.json()["id"]

        listed = client.get("/api/strategies")
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        fetched = client.get(f"/api/strategies/{strategy_id}")
        assert fetched.status_code == 200
        assert fetched.json()["name"] == "NFL Week 1"

        updated = client.put(
            f"/api/strategies/{strategy_id}", json={"bet_size": 75.0}
        )
        assert updated.status_code == 200
        assert updated.json()["bet_size"] == 75.0
        assert updated.json()["odds_american"] == -110

        deleted = client.delete(f"/api/strategies/{strategy_id}")
        assert deleted.status_code == 204
        assert client.get(f"/api/strategies/{strategy_id}").status_code == 404

    def test_missing_strategy_returns_404(self, client) -> None:
        assert client.get("/api/strategies/999").status_code == 404
        assert client.put("/api/strategies/999", json={"name": "x"}).status_code == 404
        assert client.delete("/api/strategies/999").status_code == 404

    def test_simulate_from_saved_strategy(self, client) -> None:
        strategy_id = client.post("/api/strategies", json=self._strategy()).json()["id"]

        response = client.post(f"/api/simulate/{strategy_id}")
        assert response.status_code == 200
        assert response.json()["metrics"]["risk_of_ruin"] >= 0.0

        # override num_simulations via body
        smaller = client.post(
            f"/api/simulate/{strategy_id}", json={"num_simulations": 200}
        )
        assert smaller.status_code == 200

    def test_simulate_unknown_strategy_404(self, client) -> None:
        assert client.post("/api/simulate/999").status_code == 404


class TestSystemPlays:
    def test_well_calibrated_within_tolerance(self, client) -> None:
        payload = {
            "odds_american": -110,
            "win_probability": 0.60,
            "bankroll": 1000.0,
            "bet_size": 100.0,
            "num_bets": 100,
            "num_simulations": 10000,
            "seed": 42,
        }
        response = client.post("/api/system-plays", json=payload)
        assert response.status_code == 200
        body = response.json()

        # draws are generated AT the stated probability, so the observed rate
        # must sit well inside statistical tolerance for this sample size
        assert body["calibration_status"] == "well_calibrated"
        assert body["calibration_error"] < 0.02
        assert (
            body["confidence_interval_low"]
            <= body["actual_win_rate"]
            <= body["confidence_interval_high"]
        )

    def test_calibration_result_persisted(self, db, client) -> None:
        from crud.system_plays import list_calibration_results

        payload = {
            "odds_american": -110,
            "win_probability": 0.60,
            "bankroll": 1000.0,
            "bet_size": 100.0,
            "num_bets": 100,
            "num_simulations": 5000,
            "seed": 7,
        }
        response = client.post("/api/system-plays", json=payload)
        assert response.status_code == 200

        rows = list_calibration_results(db)
        assert len(rows) == 1
        assert rows[0].stated_probability == pytest.approx(0.6)

    def test_validation_error(self, client) -> None:
        bad = {
            "odds_american": -110,
            "win_probability": 2.0,
            "bankroll": 1000.0,
            "bet_size": 100.0,
        }
        assert client.post("/api/system-plays", json=bad).status_code == 422


class TestParlay:
    def _payload(self, **overrides):
        base = {
            "legs": [
                {"odds_american": -110, "win_probability": 0.55},
                {"odds_american": -110, "win_probability": 0.55},
                {"odds_american": 150, "win_probability": 0.40},
            ],
            "bankroll": 1000.0,
            "bet_size": 50.0,
            "bet_size_type": "flat",
            "num_bets": 1,
            "num_simulations": 1000,
            "seed": 42,
        }
        base.update(overrides)
        return base

    def test_combined_math_is_exact(self, client) -> None:
        response = client.post("/api/parlay/simulate", json=self._payload())
        assert response.status_code == 200
        body = response.json()

        expected_prob = 0.55 * 0.55 * 0.40
        d110 = (100 + 110) / 110  # -110 -> 1.909090...
        expected_decimal = d110 * d110 * 2.5  # two -110 legs and one +150 leg
        assert body["combined_probability"] == pytest.approx(expected_prob)
        assert body["combined_decimal_odds"] == pytest.approx(expected_decimal)
        assert body["break_even_probability"] == pytest.approx(1 / expected_decimal)
        ev = expected_prob * (expected_decimal - 1) - (1 - expected_prob)
        assert body["ev_per_unit"] == pytest.approx(ev)

    def test_single_leg_parlay_rejected(self, client) -> None:
        legs = [{"odds_american": -110, "win_probability": 0.55}]
        response = client.post("/api/parlay/simulate", json=self._payload(legs=legs))
        assert response.status_code == 422

    def test_parlay_metrics_present(self, client) -> None:
        body = client.post("/api/parlay/simulate", json=self._payload()).json()
        assert body["run_id"] > 0
        assert 0.0 <= body["metrics"]["risk_of_ruin"] <= 1.0
        assert sum(body["distribution"]["counts"]) == 1000
