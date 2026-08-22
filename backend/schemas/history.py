from datetime import datetime

from pydantic import BaseModel


class RunSummary(BaseModel):
    """Aggregated view of a persisted simulation run for the history table."""

    run_id: int
    strategy_id: int | None
    odds_american: int | None
    win_probability: float | None
    bankroll: float | None
    bet_size: float | None
    bet_size_type: str | None
    num_bets: int | None
    num_simulations: int | None
    created_at: datetime | None
    result_count: int = 0
    win_pct: float | None = None
    avg_final_bankroll: float | None = None
    risk_of_ruin: float | None = None


class RunListResponse(BaseModel):
    runs: list[RunSummary]
