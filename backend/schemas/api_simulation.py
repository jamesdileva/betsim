from datetime import datetime

from pydantic import BaseModel, Field, field_validator

BET_SIZE_TYPES = ("flat", "percentage", "kelly", "half_kelly")


class SimulationRequest(BaseModel):
    """Parameters for a Monte Carlo simulation batch."""

    odds_american: int
    win_probability: float = Field(gt=0.0, lt=1.0)
    bankroll: float = Field(gt=0.0)
    bet_size: float = Field(gt=0.0)
    bet_size_type: str = "flat"
    num_bets: int = Field(default=100, ge=1, le=10_000)
    num_simulations: int = Field(default=5000, ge=100, le=100_000)
    seed: int | None = None

    @field_validator("odds_american")
    @classmethod
    def odds_must_be_valid(cls, v: int) -> int:
        if v == 0 or abs(v) < 100:
            raise ValueError("American odds must have magnitude >= 100 (e.g. -110, +150)")
        return v

    @field_validator("bet_size_type")
    @classmethod
    def bet_size_type_must_be_known(cls, v: str) -> str:
        if v not in BET_SIZE_TYPES:
            raise ValueError(f"bet_size_type must be one of {BET_SIZE_TYPES}")
        return v


class MetricSummary(BaseModel):
    win_pct: float
    avg_ending_bankroll: float
    median_ending_bankroll: float
    std_dev: float
    min_bankroll: float
    max_bankroll: float
    risk_of_ruin: float
    avg_max_drawdown: float
    worst_case_drawdown: float
    ev_per_bet: float
    ev_total: float


class DistributionData(BaseModel):
    bin_edges: list[float]
    counts: list[int]


class TrajectoryBands(BaseModel):
    p10: list[float]
    median: list[float]
    p90: list[float]
    min: list[float]
    max: list[float]


class SimulationResponse(BaseModel):
    run_id: int
    metrics: MetricSummary
    distribution: DistributionData
    trajectory: TrajectoryBands
    created_at: datetime | None = None
