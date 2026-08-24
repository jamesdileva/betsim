from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    """Model-ready feature vector keyed by FEATURE_NAMES entries."""

    features: dict[str, float | None] = Field(default_factory=dict)


class PredictionRequest(BaseModel):
    """Request a probability from a pluggable model source.

    source=user_input requires win_probability; source=stub ignores it.
    `side` declares whose win probability `win_probability` expresses
    (stored internally as home-team probability either way).
    Provide game_id to extract features from a stored game (features feed
    explainability); otherwise odds_american supplies the market baseline.
    """

    source: str = "user_input"
    win_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    side: str = "home"
    game_id: str | None = None
    odds_american: int | None = None
    model_id: str | None = None  # registry id for persisting the prediction

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "user_input",
                    "win_probability": 0.62,
                    "side": "home",
                    "game_id": "game-abc-123",
                }
            ]
        }
    }


class FactorOut(BaseModel):
    feature: str
    label: str
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    probability: float  # home-team win probability (storage convention)
    confidence: float
    side: str
    side_probability: float
    fair_odds_decimal: float
    ev_vs_market: float | None = None
    top_factors: list[FactorOut]
    features_used: int
