import pytest

from crud.ml_models import save_model, save_prediction
from crud.odds import save_game, save_team
from ml.portfolio import BAND_RULES, build_portfolio, score_predictions
from models import Game, ModelPrediction
from schemas.game import GameCreate, TeamCreate
from schemas.ml_model import MlModelCreate, ModelPredictionCreate


@pytest.fixture()
def model(db):
    return save_model(db, MlModelCreate(id="m1", name="stub"))


def _add_game_with_prediction(
    db, game_id: str, prob: float, confidence: float | None = None
) -> None:
    home = save_team(db, TeamCreate(name=f"{game_id}-home", sport="s"))
    away = save_team(db, TeamCreate(name=f"{game_id}-away", sport="s"))
    save_game(
        db,
        GameCreate(
            id=game_id,
            sport="s",
            home_team_id=home.id,
            away_team_id=away.id,
            status="scheduled",
        ),
    )
    save_prediction(
        db,
        ModelPredictionCreate(
            model_id="m1",
            game_id=game_id,
            predicted_probability=prob,
            fair_odds_decimal=round(1 / prob, 4),
            confidence=confidence,
        ),
    )


def test_score_predictions_ranks_descending(db, model) -> None:
    _add_game_with_prediction(db, "g-low", 0.45)
    _add_game_with_prediction(db, "g-high", 0.80)
    pairs = [
        (p, g)
        for p, g in db.query(ModelPrediction, Game).all()
    ]
    scored = score_predictions(db, pairs)
    scores = [s.score.score for s in scored]
    assert scores == sorted(scores, reverse=True)


def test_build_portfolio_allocates_by_bands_and_caps_exposure(db, model) -> None:
    # enough high-probability picks to hit band caps
    for i in range(5):
        _add_game_with_prediction(db, f"hi-{i}", 0.85)
    for i in range(3):
        _add_game_with_prediction(db, f"mid-{i}", 0.62)

    saved, scored = build_portfolio(db, bankroll=1000.0, model_id=model.id)

    assert len(items := saved.items) > 0
    total_stake = sum(i.stake for i in items)
    max_budget = (
        BAND_RULES["high"]["bankroll_share"] * 1000.0
        + BAND_RULES["medium"]["bankroll_share"] * 1000.0
        + BAND_RULES["long_shot"]["bankroll_share"] * 1000.0
    )
    assert total_stake <= min(max_budget, 800.0) + 0.01

    bands = {i.confidence_level for i in items}
    assert bands <= set(BAND_RULES.keys())

    # high-band picks capped at 2 per the rules
    high_count = sum(1 for i in items if i.confidence_level == "high")
    assert high_count <= BAND_RULES["high"]["max_bets"]

    assert len(scored) == 8


def test_build_portfolio_persists_items(db, model) -> None:
    _add_game_with_prediction(db, "g-1", 0.9)
    saved, _ = build_portfolio(db, bankroll=500.0, model_id=model.id)

    from crud.portfolios import get_portfolio_items

    rows = get_portfolio_items(db, saved.id)
    assert len(rows) == len(saved.items)
    assert all(r.portfolio_id == saved.id for r in rows)


def test_low_scores_excluded_from_portfolio(db, model) -> None:
    _add_game_with_prediction(db, "g-bad", 0.30)
    saved, scored = build_portfolio(db, bankroll=1000.0, model_id=model.id)
    assert all(s.score.score < 55 for s in scored)
    assert saved.items == []
