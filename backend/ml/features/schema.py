"""Feature definitions for the ML pipeline (Sprint 9: schema only).

Features are grouped by data source. Odds-derived and time-based features are
computable today; team-history and injury features require future data
collection sprints and extract to None until then.
"""

FEATURES: dict[str, str] = {
    # odds-derived
    "home_odds_american": "Latest home moneyline price (American)",
    "away_odds_american": "Latest away moneyline price (American)",
    "home_odds_decimal": "Home decimal odds",
    "away_odds_decimal": "Away decimal odds",
    "home_implied_prob": "Bookmaker-implied win probability for home side",
    "away_implied_prob": "Bookmaker-implied win probability for away side",
    "no_vig_home_prob": "Vig-free home probability (normalized two-way)",
    "no_vig_away_prob": "Vig-free away probability (normalized two-way)",
    "vig_total": "Sum of implied probabilities minus 1 (bookmaker margin)",
    "best_home_price": "Best (highest) American price available for home",
    "best_away_price": "Best American price available for away",
    "price_spread_home": "Max-min American price spread across books, home",
    # time-based
    "hours_until_game": "Hours from fetch time to kickoff",
    "is_weekend_game": "1 if the game falls on Sat/Sun",
    "hour_of_day": "Local hour of kickoff",
    # team history (requires historical results; None until Sprint 12+)
    "home_win_rate_10": "Home team win rate over last 10 games",
    "away_win_rate_10": "Away team win rate over last 10 games",
    "home_points_avg": "Home team average points scored",
    "away_points_avg": "Away team average points scored",
    "home_points_allowed_avg": "Home team average points allowed",
    "away_points_allowed_avg": "Away team average points allowed",
    "rest_days_home": "Days since home team's previous game",
    "rest_days_away": "Days since away team's previous game",
    "is_home_back_to_back": "1 if home team played the previous day",
    "is_away_back_to_back": "1 if away team played the previous day",
    # injuries (requires injury feed; None in MVP)
    "home_injuries_count": "Number of injured players on home team",
    "away_injuries_count": "Number of injured players on away team",
    "home_key_player_out": "1 if a high-impact player is out at home",
    "away_key_player_out": "1 if a high-impact player is out away",
    # line movement (requires multi-snapshot history)
    "line_movement_hours": "American-price change over trailing window, home",
    "books_count": "Number of bookmakers quoting this game",
}

FEATURE_NAMES = list(FEATURES.keys())
