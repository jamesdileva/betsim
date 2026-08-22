from pydantic import BaseModel, Field, field_validator

from schemas.api_simulation import DistributionData, MetricSummary


class ParlayLeg(BaseModel):
    odds_american: int
    win_probability: float = Field(gt=0.0, lt=1.0)

    @field_validator("odds_american")
    @classmethod
    def odds_must_be_valid(cls, v: int) -> int:
        if v == 0 or abs(v) < 100:
            raise ValueError("American odds must have magnitude >= 100 (e.g. -110, +150)")
        return v


class ParlayRequest(BaseModel):
    legs: list[ParlayLeg] = Field(min_length=2, max_length=10)
    bankroll: float = Field(gt=0.0)
    bet_size: float = Field(gt=0.0)
    bet_size_type: str = "flat"
    num_bets: int = Field(default=1, ge=1, le=100)
    num_simulations: int = Field(default=5000, ge=100, le=100_000)
    seed: int | None = None

    @field_validator("bet_size_type")
    @classmethod
    def bet_size_type_must_be_known(cls, v: str) -> str:
        if v not in ("flat", "percentage", "kelly", "half_kelly"):
            raise ValueError("bet_size_type must be flat/percentage/kelly/half_kelly")
        return v


class ParlayResponse(BaseModel):
    combined_probability: float
    combined_decimal_odds: float
    ev_per_unit: float
    break_even_probability: float
    run_id: int
    metrics: MetricSummary
    distribution: DistributionData
