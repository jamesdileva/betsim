"""Explainability: human-readable top factors behind a prediction.

MVP attribution is heuristic and clearly labeled as such — there is no
trained model to introspect yet. Factors are scored by signed impact:
positive values push the predicted probability UP (favor the home side),
negative values push it DOWN.
"""

from ml.features.schema import FEATURE_NAMES

# group importance used to scale raw feature magnitudes into comparable weights
GROUP_WEIGHTS: dict[str, float] = {
    "model_edge_vs_market": 1.0,
    "home_odds_american": 0.6,
    "away_odds_american": 0.4,
    "no_vig_home_prob": 0.8,
    "vig_total": 0.2,
    "hours_until_game": 0.15,
    "is_weekend_game": 0.1,
    "hour_of_day": 0.05,
    "books_count": 0.1,
}

_LABELS: dict[str, str] = {
    "model_edge_vs_market": "Model edge vs. market",
    "home_odds_american": "Home moneyline price",
    "away_odds_american": "Away moneyline price",
    "no_vig_home_prob": "Market fair probability (home)",
    "vig_total": "Bookmaker vig",
    "hours_until_game": "Time until kickoff",
    "is_weekend_game": "Weekend game",
    "hour_of_day": "Kickoff hour",
    "books_count": "Bookmaker coverage",
}


def explain_prediction(
    features: dict[str, float | None],
    predicted_probability: float | None = None,
    *,
    top_n: int = 5,
) -> list[dict]:
    """Return the top-N factors with signed weights, sorted by |impact|.

    Every returned item: {feature, label, impact, direction} where direction
    is "+" when the factor pushes the probability up and "-" when down.
    """
    factors: list[dict] = []

    market_prob = features.get("no_vig_home_prob")
    if (
        predicted_probability is not None
        and isinstance(market_prob, (int, float))
        and market_prob is not None
    ):
        delta = predicted_probability - float(market_prob)
        factors.append(
            {
                "feature": "model_edge_vs_market",
                "label": _LABELS["model_edge_vs_market"],
                "impact": round(delta, 4),
                "direction": "+" if delta >= 0 else "-",
            }
        )

    for name in FEATURE_NAMES:
        value = features.get(name)
        weight = GROUP_WEIGHTS.get(name)
        if name == "model_edge_vs_market" or weight is None or value is None:
            continue
        normalized = float(value)
        # squash large raw magnitudes (odds prices, hours) into [-1, 1]
        impact = max(-1.0, min(1.0, normalized / 200.0)) * weight
        if impact == 0.0:
            continue
        factors.append(
            {
                "feature": name,
                "label": _LABELS.get(name, name.replace("_", " ").title()),
                "impact": round(impact, 4),
                "direction": "+" if impact > 0 else "-",
            }
        )

    factors.sort(key=lambda f: abs(f["impact"]), reverse=True)
    return factors[:top_n]
