from pathlib import Path

from sqlalchemy import inspect

import models  # noqa: F401 - register all tables with Base.metadata
from database import Base
from models import (
    Game,
    GameOdds,
    MlModel,
    Portfolio,
    PortfolioItem,
    SimulationResult,
    SimulationRun,
    Strategy,
    SystemPlayResult,
    Team,
)

EXPECTED_TABLES = {
    "backtest_results",
    "game_odds",
    "games",
    "injuries",
    "ml_models",
    "model_evaluations",
    "model_predictions",
    "portfolio_items",
    "portfolios",
    "raw_injuries",
    "raw_odds",
    "simulation_results",
    "simulation_runs",
    "strategies",
    "system_play_results",
    "teams",
}


def test_metadata_defines_all_16_tables() -> None:
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES


def test_create_all_creates_all_tables(db_session) -> None:
    inspector = inspect(db_session.bind)
    assert set(inspector.get_table_names()) == EXPECTED_TABLES


def test_team_game_relationship(db_session) -> None:
    home = Team(name="Boston Bruins", sport="hockey", league="NHL")
    away = Team(name="Toronto Maple Leafs", sport="hockey", league="NHL")
    db_session.add_all([home, away])
    db_session.flush()

    game = Game(id="game-123", sport="hockey", home_team=home, away_team=away)
    db_session.add(game)
    db_session.commit()

    fetched = db_session.get(Game, "game-123")
    assert fetched.home_team.name == "Boston Bruins"
    assert fetched.away_team.name == "Toronto Maple Leafs"
    assert game.id in {g.id for g in home.home_games}


def test_strategy_simulation_run_relationship(db_session) -> None:
    strategy = Strategy(
        name="NFL Week 1",
        odds_american=-110,
        win_probability=0.55,
        bankroll=1000,
        bet_size=50,
        bet_size_type="flat",
        num_bets=100,
        num_simulations=5000,
    )
    db_session.add(strategy)
    db_session.flush()

    run = SimulationRun(strategy=strategy, num_simulations=5000, seed=42)
    db_session.add(run)
    db_session.flush()

    db_session.add_all(
        [
            SimulationResult(simulation_run=run, run_index=i, final_bankroll=1000 + i)
            for i in range(3)
        ]
    )
    db_session.commit()

    fetched = db_session.get(Strategy, strategy.id)
    assert len(fetched.simulation_runs) == 1
    assert len(fetched.simulation_runs[0].results) == 3


def test_ml_model_prediction_and_portfolio_relationships(db_session) -> None:
    team_a = Team(name="A", sport="nba", league="NBA")
    team_b = Team(name="B", sport="nba", league="NBA")
    db_session.add_all([team_a, team_b])
    db_session.flush()

    game = Game(id="g-1", sport="nba", home_team=team_a, away_team=team_b)
    model = MlModel(id="model-v1", name="stub", version="1")
    db_session.add_all([game, model])
    db_session.flush()

    portfolio = Portfolio(model=model)
    item = PortfolioItem(
        portfolio=portfolio, game=game, model=model, confidence_level="high"
    )
    system_play = SystemPlayResult(stated_probability=0.6, actual_win_rate=0.598)
    odds = GameOdds(game=game, sportsbook="draftkings", market_type="moneyline")
    db_session.add_all([item, portfolio, system_play, odds])
    db_session.commit()

    fetched_model = db_session.get(MlModel, "model-v1")
    assert fetched_model.predictions == []
    assert fetched_model.evaluations == []
    fetched_portfolio = db_session.query(Portfolio).one()
    assert len(fetched_portfolio.items) == 1
    assert fetched_portfolio.items[0].game_id == "g-1"


def test_foreign_keys_enforced(db_session) -> None:
    inspector = inspect(db_session.bind)
    fks = {
        fk["constrained_columns"][0]: fk["referred_table"]
        for table in EXPECTED_TABLES
        for fk in inspector.get_foreign_keys(table)
        if len(fk["constrained_columns"]) == 1
    }
    assert fks["home_team_id"] == "teams"
    assert fks["away_team_id"] == "teams"
    assert fks["strategy_id"] == "strategies"
    assert fks["simulation_run_id"] == "simulation_runs"
    assert fks["game_id"] == "games"
    assert fks["model_id"] == "ml_models"
    assert fks["portfolio_id"] == "portfolios"


def test_query_heavy_columns_are_indexed(db_session) -> None:
    inspector = inspect(db_session.bind)
    indexed = {
        (col,): True
        for table in EXPECTED_TABLES
        for idx in inspector.get_indexes(table)
        for col in idx["column_names"]
        if col
    }
    required = [
        ("sport",),
        ("game_time",),
        ("status",),
        ("season",),
        ("created_at",),
        ("final_bankroll",),
    ]
    for column in required:
        assert tuple(column) in indexed, f"missing index on {column}"


def test_alembic_upgrade_head_on_empty_db(tmp_path: Path) -> None:
    from alembic import command
    from alembic.config import Config

    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{tmp_path / 'mig.db'}")

    command.upgrade(config, "head")

    conn = inspect(__import__("sqlalchemy").create_engine(f"sqlite:///{tmp_path / 'mig.db'}"))
    tables = set(conn.get_table_names()) - {"alembic_version"}
    assert tables == EXPECTED_TABLES
