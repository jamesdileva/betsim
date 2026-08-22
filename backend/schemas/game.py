from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(max_length=100)
    sport: str = Field(max_length=20)
    league: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=50)
    abbreviation: str | None = Field(default=None, max_length=10)


class GameCreate(BaseModel):
    id: str = Field(max_length=100)
    sport: str = Field(max_length=20)
    league: str | None = None
    home_team_id: int | None = None
    away_team_id: int | None = None
    home_score: int | None = None
    away_score: int | None = None
    game_time: datetime | None = None
    status: str = "scheduled"
    season: str | None = None
    week: int | None = None
    venue: str | None = None


class GameOddsCreate(BaseModel):
    game_id: str
    sportsbook: str | None = None
    market_type: str | None = None
    outcome_name: str | None = None
    odds_american: int | None = None
    odds_decimal: float | None = None
    implied_probability: float | None = None
    is_no_vig: bool = False
    timestamp: datetime | None = None


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sport: str
    league: str | None
    home_team_id: int | None
    away_team_id: int | None
    home_score: int | None
    away_score: int | None
    game_time: datetime | None
    status: str | None
    season: str | None
    week: int | None
    venue: str | None
    created_at: datetime


class GameOddsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_id: str
    sportsbook: str | None
    market_type: str | None
    outcome_name: str | None
    odds_american: int | None
    odds_decimal: float | None
    implied_probability: float | None
    is_no_vig: bool
    timestamp: datetime | None
    created_at: datetime
