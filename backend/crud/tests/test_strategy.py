import pytest

import crud.strategy as strategy_crud
from schemas.strategy import StrategyCreate, StrategyUpdate


@pytest.fixture()
def sample() -> StrategyCreate:
    return StrategyCreate(
        name="NFL Week 1 -5",
        odds_american=-110,
        win_probability=0.55,
        bankroll=1000.0,
        bet_size=50.0,
        bet_size_type="flat",
        num_bets=100,
        num_simulations=5000,
    )


def test_save_returns_pydantic_model(db, sample) -> None:
    saved = strategy_crud.save_strategy(db, sample)
    assert isinstance(saved, type(sample).__mro__[-2]) or hasattr(saved, "model_dump")
    assert saved.id is not None
    assert saved.created_at is not None
    assert saved.name == "NFL Week 1 -5"


def test_get_strategy(db, sample) -> None:
    saved = strategy_crud.save_strategy(db, sample)
    fetched = strategy_crud.get_strategy(db, saved.id)
    assert fetched is not None
    assert fetched.name == sample.name
    assert fetched.win_probability == pytest.approx(0.55)


def test_get_missing_returns_none(db) -> None:
    assert strategy_crud.get_strategy(db, 9999) is None


def test_list_orders_newest_first(db, sample) -> None:
    first = strategy_crud.save_strategy(db, sample)
    second = strategy_crud.save_strategy(
        db, sample.model_copy(update={"name": "Second"})
    )
    listed = strategy_crud.list_strategies(db)
    assert [s.id for s in listed] == [second.id, first.id]


def test_update_partial_fields_only(db, sample) -> None:
    saved = strategy_crud.save_strategy(db, sample)
    updated = strategy_crud.update_strategy(
        db, saved.id, StrategyUpdate(bet_size=75.0)
    )
    assert updated is not None
    assert updated.bet_size == 75.0
    assert updated.odds_american == sample.odds_american
    assert updated.num_bets == sample.num_bets


def test_update_missing_returns_none(db) -> None:
    assert strategy_crud.update_strategy(db, 9999, StrategyUpdate(name="x")) is None


def test_delete_round_trip(db, sample) -> None:
    saved = strategy_crud.save_strategy(db, sample)
    assert strategy_crud.delete_strategy(db, saved.id) is True
    assert strategy_crud.get_strategy(db, saved.id) is None
    assert strategy_crud.delete_strategy(db, saved.id) is False
