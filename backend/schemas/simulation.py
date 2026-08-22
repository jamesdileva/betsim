from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SimulationRunCreate(BaseModel):
    strategy_id: int | None = None
    odds_american: int
    win_probability: float = Field(ge=0.0, le=1.0)
    bankroll: float = Field(gt=0.0)
    bet_size: float = Field(gt=0.0)
    bet_size_type: str
    num_bets: int = Field(ge=1)
    num_simulations: int = Field(ge=1)
    seed: int | None = None


class SimulationResultCreate(BaseModel):
    run_index: int
    final_bankroll: float
    is_profitable: bool | None = None
    max_drawdown: float | None = None


class SimulationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    strategy_id: int | None
    odds_american: int | None
    win_probability: float | None
    bankroll: float | None
    bet_size: float | None
    bet_size_type: str | None
    num_bets: int | None
    num_simulations: int | None
    seed: int | None
    created_at: datetime


class SimulationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    simulation_run_id: int
    run_index: int | None
    final_bankroll: float | None
    is_profitable: bool | None
    max_drawdown: float | None
    created_at: datetime
