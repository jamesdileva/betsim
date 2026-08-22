from pydantic import BaseModel, Field, field_validator

BET_SIZE_TYPES = ("flat", "percentage", "kelly", "half_kelly")


class SystemPlaysRequest(BaseModel):
    """Calibration request: stated probability vs. simulated reality."""

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


class CalibrationReport(BaseModel):
    stated_probability: float
    actual_win_rate: float
    calibration_error: float
    calibration_status: str
    confidence_interval_low: float
    confidence_interval_high: float
    recommendation: str
