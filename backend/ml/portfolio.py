"""Portfolio construction: confidence-band allocation over scored predictions.

Algorithm (Product Design section 10):
  1. Score every scheduled-game prediction via the Intelligence Score
  2. Rank by score descending
  3. Allocate by band: High (>=85) 2 bets / 40% of bankroll,
     Medium (70-84) 4 bets / 30%, Long Shot (55-69) 6 bets / 20%
  4. Per-bet stake from Kelly, capped at the band's per-bet share
  5. Total exposure capped at 80% of bankroll
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from crud.portfolios import save_portfolio
from ml.recommend import IntelligenceScoreResult, calculate_intelligence_score
from models import Game, ModelPrediction
from schemas.portfolio import PortfolioCreate, PortfolioItemCreate, PortfolioRead
from simulation.kelly import kelly_criterion

BAND_RULES: dict[str, dict] = {
    "high": {"min_score": 85, "max_bets": 2, "bankroll_share": 0.40},
    "medium": {"min_score": 70, "max_bets": 4, "bankroll_share": 0.30},
    "long_shot": {"min_score": 55, "max_bets": 6, "bankroll_share": 0.20},
}

MAX_EXPOSURE = 0.80


@dataclass
class ScoredPrediction:
    prediction: ModelPrediction
    game: Game | None
    score: IntelligenceScoreResult


def _band_for(score: int) -> str | None:
    for band, rules in BAND_RULES.items():
        if score >= rules["min_score"]:
            return band
    return None  # below 55: do not include


def _simulation_win_rate(db: Session, model_id: str, predicted_prob: float) -> float:
    """Observed backtest accuracy when available; otherwise the raw prediction."""
    from ml.backtest import evaluate_model  # noqa: F401 - documents the feedback source
    from models import ModelEvaluation

    latest_eval = (
        db.query(ModelEvaluation)
        .filter(ModelEvaluation.model_id == model_id)
        .order_by(ModelEvaluation.evaluated_at.desc())
        .first()
    )
    if latest_eval is not None and latest_eval.accuracy is not None:
        return max(0.0, min(1.0, float(latest_eval.accuracy)))
    return predicted_prob


def score_predictions(
    db: Session,
    predictions: list[tuple[ModelPrediction, Game | None]],
) -> list[ScoredPrediction]:
    scored: list[ScoredPrediction] = []
    for prediction, game in predictions:
        p = float(prediction.predicted_probability)
        sim_rate = _simulation_win_rate(db, prediction.model_id, p)
        ev = float(prediction.ev) if prediction.ev is not None else p * (
            float(prediction.fair_odds_decimal) if prediction.fair_odds_decimal else 2.0
        ) - 1.0
        calibration_status = "well_calibrated"
        result = calculate_intelligence_score(
            predicted_prob=p,
            simulation_win_rate=sim_rate,
            ev=max(-1.0, ev),
            model_confidence=(
                float(prediction.confidence) if prediction.confidence is not None else 0.5
            ),
            calibration_status=calibration_status,
        )
        scored.append(ScoredPrediction(prediction=prediction, game=game, score=result))
    scored.sort(key=lambda s: s.score.score, reverse=True)
    return scored


def build_portfolio(
    db: Session, bankroll: float, model_id: str | None = None
) -> tuple[PortfolioRead, list[ScoredPrediction]]:
    """Construct and persist today's portfolio. Returns (saved, scored)."""
    query = (
        db.query(ModelPrediction, Game)
        .outerjoin(Game, ModelPrediction.game_id == Game.id)
        .filter(Game.status.is_(None) | (Game.status != "final"))
    )
    if model_id is not None:
        query = query.filter(ModelPrediction.model_id == model_id)
    predictions = query.all()

    scored = score_predictions(db, predictions)

    items: list[PortfolioItemCreate] = []
    total_staked = 0.0
    exposure_cap = bankroll * MAX_EXPOSURE

    for band, rules in BAND_RULES.items():
        candidates = [s for s in scored if _band_for(s.score.score) == band]
        picked = candidates[: rules["max_bets"]]
        if not picked:
            continue
        band_budget = bankroll * rules["bankroll_share"]
        per_bet_cap = band_budget / len(picked)
        for candidate in picked:
            if total_staked >= exposure_cap:
                break
            p = float(candidate.prediction.predicted_probability)
            stored_dec = candidate.prediction.fair_odds_decimal
            fair_dec = (
                float(stored_dec)
                if stored_dec is not None and stored_dec > 1
                else 1.0 / max(p, 0.01)
            )
            stake = kelly_criterion(fair_dec, p) * bankroll
            stake = min(stake, per_bet_cap, exposure_cap - total_staked)
            if stake <= 0:
                continue
            items.append(
                PortfolioItemCreate(
                    game_id=candidate.prediction.game_id,
                    model_id=candidate.prediction.model_id,
                    confidence_level=band,
                    bet_type="moneyline",
                    stake=round(stake, 2),
                    predicted_probability=p,
                    ev=candidate.prediction.ev,
                    recommendation_stars=candidate.score.stars,
                )
            )
            total_staked += stake

    portfolio = PortfolioCreate(
        total_risk=round(total_staked / bankroll * 100.0, 2) if bankroll > 0 else 0.0,
        expected_roi=None,
        kelly_exposure=round(total_staked / bankroll * 100.0, 2) if bankroll > 0 else 0.0,
        model_id=model_id,
        items=items,
    )
    saved = save_portfolio(db, portfolio)
    return saved, scored
