"""Model registry + prediction endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.ml_models import get_model, list_models, save_prediction
from ml.explainability import explain_prediction
from ml.features.engineering import extract_features
from ml.models.stub import StubModel
from ml.models.user_input import UserInputModel
from models import Game, GameOdds
from schemas.model import FactorOut, PredictionRequest, PredictionResponse

router = APIRouter()

SOURCES = ("user_input", "stub")
SIDES = ("home", "away")


def _home_probability(request: PredictionRequest) -> float:
    """Convert the requested side's probability to home-team convention.

    An away-side claim of 40% IS a home-side claim of 60% - storing it raw
    inverts the pick (real incident: a correct Pirates read was graded as a
    Dodgers miss).
    """
    if request.win_probability is None:
        return 0.5
    if request.side == "away":
        return 1.0 - request.win_probability
    return request.win_probability


def _build_model(request: PredictionRequest, home_probability: float):
    if request.source == "user_input":
        if request.win_probability is None:
            raise HTTPException(
                status_code=422,
                detail="source=user_input requires win_probability",
            )
        return UserInputModel(
            probability=home_probability,
            confidence=request.confidence if request.confidence is not None else 0.5,
        )
    if request.source == "stub":
        return StubModel(
            probability=home_probability,
            confidence=request.confidence or 0.5,
        )
    raise HTTPException(status_code=422, detail=f"source must be one of {SOURCES}")


def _features_for(db: Session, game_id: str) -> dict[str, float | None]:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    odds_rows = (
        db.query(GameOdds).filter(GameOdds.game_id == game_id).limit(200).all()
    )
    return extract_features(game, odds_rows)


@router.post("/models/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest, db: Annotated[Session, Depends(get_db)]
) -> PredictionResponse:
    if request.side not in SIDES:
        raise HTTPException(status_code=422, detail=f"side must be one of {SIDES}")
    home_probability = _home_probability(request)
    model = _build_model(request, home_probability)

    features: dict[str, float | None] = {}
    market_decimal: float | None = None
    if request.game_id:
        features = _features_for(db, request.game_id)
        market_dec = features.get("home_odds_decimal")
        market_decimal = float(market_dec) if isinstance(market_dec, (int, float)) else None
    elif request.odds_american is not None:
        from simulation.odds import OddsConversion

        market_decimal = OddsConversion.american_to_decimal(request.odds_american)

    probability = model.clamp(model.predict(features))
    confidence = model.clamp(model.get_confidence(features))
    side_probability = (
        home_probability if request.side == "home" else 1.0 - home_probability
    )
    fair_odds = 1.0 / probability if probability > 0 else float("inf")
    ev_vs_market = probability * market_decimal - 1.0 if market_decimal else None

    top_factors = explain_prediction(features, probability, top_n=5)

    # persist through the registry when the caller names a registered model
    if request.model_id and get_model(db, request.model_id):
        if not request.game_id:
            raise HTTPException(
                status_code=422,
                detail="model_id persistence requires game_id",
            )
        save_prediction(
            db,
            _prediction_create(
                model_id=request.model_id,
                game_id=request.game_id,
                probability=probability,
                confidence=confidence,
                fair_odds=fair_odds,
                ev=ev_vs_market,
            ),
        )

    return PredictionResponse(
        probability=probability,
        confidence=confidence,
        side=request.side,
        side_probability=side_probability,
        fair_odds_decimal=fair_odds,
        ev_vs_market=ev_vs_market,
        top_factors=[FactorOut(**f) for f in top_factors],
        features_used=sum(1 for v in features.values() if v is not None),
    )


def _prediction_create(
    *,
    model_id: str,
    game_id: str,
    probability: float,
    confidence: float,
    fair_odds: float,
    ev: float | None,
):
    from schemas.ml_model import ModelPredictionCreate

    return ModelPredictionCreate(
        model_id=model_id,
        game_id=game_id,
        predicted_probability=probability,
        confidence=confidence,
        fair_odds_decimal=fair_odds,
        ev=ev,
    )


@router.get("/models/list")
def models_list(
    db: Annotated[Session, Depends(get_db)],
    include_archived: bool = False,
) -> dict[str, Any]:
    rows = list_models(db, include_archived=include_archived)
    return {
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "is_production": m.is_production,
                "accuracy": m.accuracy,
                "roi": m.roi,
            }
            for m in rows
        ]
    }
