import pytest

from ml.explainability import explain_prediction


def _full_features() -> dict[str, float | None]:
    return {name: None for name in (
        "home_odds_american", "away_odds_american", "home_odds_decimal",
        "away_odds_decimal", "home_implied_prob", "away_implied_prob",
        "no_vig_home_prob", "no_vig_away_prob", "vig_total",
        "best_home_price", "best_away_price", "price_spread_home",
        "hours_until_game", "is_weekend_game", "hour_of_day",
    )}


def test_edge_vs_market_is_top_factor_when_present() -> None:
    features = _full_features()
    features["no_vig_home_prob"] = 0.55
    factors = explain_prediction(features, predicted_probability=0.65)
    top = factors[0]
    assert top["feature"] == "model_edge_vs_market"
    assert top["impact"] == pytest.approx(0.10, abs=1e-4)
    assert top["direction"] == "+"
    # sorted by |impact| descending
    impacts = [abs(f["impact"]) for f in factors]
    assert impacts == sorted(impacts, reverse=True)


def test_returns_at_most_five_factors_with_weights_and_signs() -> None:
    features = _full_features()
    features.update(
        {
            "no_vig_home_prob": 0.5,
            "home_odds_american": -150.0,
            "away_odds_american": 130.0,
            "hours_until_game": 48.0,
            "is_weekend_game": 1.0,
            "books_count": 8.0,
            "vig_total": 0.03,
        }
    )
    factors = explain_prediction(features, predicted_probability=0.6, top_n=5)
    assert len(factors) <= 5
    for factor in factors:
        assert set(factor.keys()) == {"feature", "label", "impact", "direction"}
        assert factor["direction"] in ("+", "-")
        assert isinstance(factor["impact"], float)


def test_negative_direction_for_low_values() -> None:
    features = _full_features()
    features["no_vig_home_prob"] = None
    features["hours_until_game"] = -24.0  # past kickoff: negative impact
    factors = explain_prediction(features, predicted_probability=None, top_n=5)
    assert any(f["feature"] == "hours_until_game" and f["direction"] == "-" for f in factors)


def test_no_factors_when_features_empty() -> None:
    assert explain_prediction({}, predicted_probability=None) == []
