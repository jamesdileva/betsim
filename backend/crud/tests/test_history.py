import pytest

from crud.simulation import (
    delete_simulation_run,
    list_run_summaries,
    save_simulation_results,
    save_simulation_run,
)
from schemas.simulation import SimulationResultCreate, SimulationRunCreate


@pytest.fixture()
def seeded_run(db):
    run = SimulationRunCreate(
        odds_american=-110,
        win_probability=0.55,
        bankroll=1000.0,
        bet_size=50.0,
        bet_size_type="flat",
        num_bets=100,
        num_simulations=4,
    )
    saved = save_simulation_run(db, run)
    results = [
        SimulationResultCreate(run_index=0, final_bankroll=1200.0, is_profitable=True),
        SimulationResultCreate(run_index=1, final_bankroll=900.0, is_profitable=False),
        SimulationResultCreate(run_index=2, final_bankroll=0.0, is_profitable=False),
        SimulationResultCreate(run_index=3, final_bankroll=1100.0, is_profitable=True),
    ]
    save_simulation_results(db, saved.id, results)
    return saved.id


def test_list_run_summaries_computes_stats(db, seeded_run) -> None:
    summaries = list_run_summaries(db)
    assert len(summaries) == 1
    s = summaries[0]
    assert s["run_id"] == seeded_run
    assert s["result_count"] == 4
    assert s["win_pct"] == pytest.approx(0.5)  # 2 of 4 profitable
    assert s["risk_of_ruin"] == pytest.approx(0.25)  # one busted run
    assert s["avg_final_bankroll"] == pytest.approx((1200 + 900 + 0 + 1100) / 4)


def test_delete_run_removes_results_too(db, seeded_run) -> None:
    assert delete_simulation_run(db, seeded_run) is True
    assert list_run_summaries(db) == []
    assert delete_simulation_run(db, seeded_run) is False
