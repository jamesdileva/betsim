import pytest

import crud.simulation as sim_crud
import crud.strategy as strategy_crud
from schemas.simulation import SimulationResultCreate, SimulationRunCreate
from schemas.strategy import StrategyCreate


@pytest.fixture()
def run_data() -> SimulationRunCreate:
    return SimulationRunCreate(
        odds_american=-110,
        win_probability=0.55,
        bankroll=1000.0,
        bet_size=50.0,
        bet_size_type="flat",
        num_bets=100,
        num_simulations=5000,
        seed=42,
    )


def test_save_run_returns_pydantic(db, run_data) -> None:
    saved = sim_crud.save_simulation_run(db, run_data)
    assert saved.id is not None
    assert saved.seed == 42


def test_save_run_with_strategy_link(db, run_data) -> None:
    strategy = strategy_crud.save_strategy(
        db, StrategyCreate(name="linked", odds_american=-110, win_probability=0.55)
    )
    saved = sim_crud.save_simulation_run(
        db, run_data.model_copy(update={"strategy_id": strategy.id})
    )
    fetched = sim_crud.get_simulation_run(db, saved.id)
    assert fetched is not None
    assert fetched.strategy_id == strategy.id


def test_bulk_insert_1000_results(db, run_data) -> None:
    saved = sim_crud.save_simulation_run(db, run_data)
    results = [
        SimulationResultCreate(run_index=i, final_bankroll=1000.0 + i, is_profitable=True)
        for i in range(1000)
    ]
    count = sim_crud.save_simulation_results(db, saved.id, results)
    assert count == 1000
    fetched = sim_crud.get_run_results(db, saved.id, limit=5)
    assert len(fetched) == 5
    assert [r.run_index for r in fetched] == [0, 1, 2, 3, 4]


def test_join_traversal_strategy_to_results(db, run_data) -> None:
    """strategy -> simulation_runs -> results join works end to end."""
    strategy = strategy_crud.save_strategy(
        db, StrategyCreate(name="traversal", odds_american=-110, win_probability=0.55)
    )
    run1 = sim_crud.save_simulation_run(
        db, run_data.model_copy(update={"strategy_id": strategy.id})
    )
    run2 = sim_crud.save_simulation_run(
        db, run_data.model_copy(update={"strategy_id": strategy.id})
    )
    for run in (run1, run2):
        sim_crud.save_simulation_results(
            db,
            run.id,
            [SimulationResultCreate(run_index=0, final_bankroll=1234.0)],
        )

    runs = sim_crud.list_runs_for_strategy(db, strategy.id)
    assert {r.id for r in runs} == {run1.id, run2.id}
    for run in runs:
        results = sim_crud.get_run_results(db, run.id)
        assert len(results) == 1
        assert results[0].final_bankroll == pytest.approx(1234.0)


def test_empty_bulk_insert_is_noop(db, run_data) -> None:
    saved = sim_crud.save_simulation_run(db, run_data)
    assert sim_crud.save_simulation_results(db, saved.id, []) == 0


def test_invalid_fk_raises_and_session_recovers(db, run_data) -> None:
    from sqlalchemy.exc import IntegrityError

    bad = run_data.model_copy(update={"strategy_id": 99999})
    with pytest.raises(IntegrityError):
        sim_crud.save_simulation_run(db, bad)

    # session must be usable again after the rollback inside the CRUD helper
    ok = sim_crud.save_simulation_run(db, run_data)
    assert ok.id is not None
