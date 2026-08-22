from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StrategyBase(BaseModel):
    name: str = Field(max_length=100)
    odds_american: int | None = None
    win_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    bankroll: float | None = Field(default=None, gt=0.0)
    bet_size: float | None = Field(default=None, gt=0.0)
    bet_size_type: str = "flat"
    num_bets: int | None = Field(default=None, ge=1)
    num_simulations: int = Field(default=5000, ge=1)
    strategy_type: str = "single"


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    odds_american: int | None = None
    win_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    bankroll: float | None = Field(default=None, gt=0.0)
    bet_size: float | None = Field(default=None, gt=0.0)
    bet_size_type: str | None = None
    num_bets: int | None = Field(default=None, ge=1)
    num_simulations: int | None = Field(default=None, ge=1)
    strategy_type: str | None = None


class StrategyRead(StrategyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = None
