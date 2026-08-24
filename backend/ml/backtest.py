"""BacktestService: replay predictions against actual game results.

A prediction becomes backtestable when its game has final scores. Each
replay creates a backtest_results row with:
  - edge = predicted_prob x fair_decimal - 1 (None when fair odds are absent)
  - roi  = per-bet return on a Kelly-sized stake (Sprint 12 test requirement)
Duplicate replays are skipped via the existing (model_id, game_id) pair.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from crud.portfolios import save_model_evaluation
from models import BacktestResult, Game, ModelEvaluation, ModelPrediction
from schemas.portfolio import ModelEvaluationCreate
from simulation.kelly import kelly_criterion
from simulation.odds import OddsConversion


def derive_outcome(game: Game) -> bool | None:
    """True = home win, False = home loss; None when not finished."""
    if game.status != "final" or game.home_score is None or game.away_score is None:
        return None
    return game.home_score > game.away_score


def _fair_decimal(
    db: Session, model_id: str, game: Game, predicted_probability: float
) -> float | None:
    """Decimal odds to grade the pick against, in priority order:

    1. Best market price for the HOME side from stored game_odds - grading
       against the real closing line is the whole point (grading against
       1/probability makes edge exactly zero by construction, which masked
       every real edge in our first live session).
    2. Fair odds stored on the prediction row.
    3. Odds implied by the probability itself (last resort).
    """
    from models import GameOdds

    if game.home_team is not None:
        rows = (
            db.query(GameOdds)
            .filter(
                GameOdds.game_id == game.id,
                GameOdds.outcome_name == game.home_team.name,
                GameOdds.odds_american.is_not(None),
            )
            .all()
        )
        if rows:
            best = max(r.odds_american for r in rows)
            return OddsConversion.american_to_decimal(best)

    prediction_row = (
        db.query(ModelPrediction)
        .filter(
            ModelPrediction.model_id == model_id,
            ModelPrediction.game_id == game.id,
        )
        .order_by(ModelPrediction.created_at.desc())
        .first()
    )
    if prediction_row is not None and prediction_row.fair_odds_decimal:
        return float(prediction_row.fair_odds_decimal)
    if 0 < predicted_probability < 1:
        return 1.0 / predicted_probability
    return None


def run_backtest(
    db: Session,
    model_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> int:
    """Replay eligible predictions into backtest_results. Returns rows created."""
    query = (
        db.query(ModelPrediction, Game)
        .join(Game, ModelPrediction.game_id == Game.id)
        .filter(Game.status == "final", Game.home_score.is_not(None), Game.away_score.is_not(None))
    )
    if model_id is not None:
        query = query.filter(ModelPrediction.model_id == model_id)
    if date_from is not None:
        query = query.filter(ModelPrediction.created_at >= date_from)
    if date_to is not None:
        query = query.filter(ModelPrediction.created_at <= date_to)

    pairs = query.all()
    created = 0
    for prediction, game in pairs:
        exists = (
            db.query(BacktestResult)
            .filter(
                BacktestResult.model_id == prediction.model_id,
                BacktestResult.game_id == prediction.game_id,
            )
            .first()
        )
        if exists is not None or prediction.predicted_probability is None:
            continue

        outcome = derive_outcome(game)
        if outcome is None:
            continue

        p = float(prediction.predicted_probability)
        fair_dec = _fair_decimal(db, prediction.model_id, game, p)

        edge = p * fair_dec - 1.0 if fair_dec is not None else None
        roi = None
        if fair_dec is not None and fair_dec > 1.0:
            stake_fraction = kelly_criterion(fair_dec, p)
            roi = stake_fraction * (fair_dec - 1.0) if outcome else -stake_fraction

        db.add(
            BacktestResult(
                model_id=prediction.model_id,
                game_id=game.id,
                predicted_probability=p,
                actual_outcome=outcome,
                edge=edge,
                roi=roi,
            )
        )
        db.commit()
        created += 1

    return created


def evaluate_model(db: Session, model_id: str) -> ModelEvaluation | None:
    """Compute accuracy / Brier / calibration error / avg ROI for a model."""
    results = (
        db.query(BacktestResult)
        .filter(BacktestResult.model_id == model_id)
        .all()
    )
    usable = [r for r in results if r.actual_outcome is not None and r.predicted_probability]
    if not usable:
        return None

    n = len(usable)
    probs = [float(r.predicted_probability) for r in usable]
    outcomes = [bool(r.actual_outcome) for r in usable]

    correct = sum(1 for r, o in zip(probs, outcomes, strict=True) if (r >= 0.5) == o)
    accuracy = correct / n

    brier = (
        sum((p - (1.0 if o else 0.0)) ** 2 for p, o in zip(probs, outcomes, strict=True)) / n
    )

    mean_predicted = sum(probs) / n
    observed_rate = sum(outcomes) / n
    calibration_error = abs(mean_predicted - observed_rate)

    rois = [float(r.roi) for r in usable if r.roi is not None]
    avg_roi = sum(rois) / len(rois) if rois else None

    evaluation = save_model_evaluation(
        db,
        ModelEvaluationCreate(
            model_id=model_id,
            accuracy=accuracy,
            calibration_error=calibration_error,
            avg_roi=avg_roi,
            brier_score=brier,
            notes=f"Backtest over {n} games",
        ),
    )
    # persist evaluated_at timestamp explicitly
    evaluation_model = (
        db.query(ModelEvaluation).filter(ModelEvaluation.id == evaluation.id).one()
    )
    evaluation_model.evaluated_at = datetime.now()
    db.commit()
    return evaluation_model

