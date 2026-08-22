from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class SimulationRun(Base):
    """A single invocation of the Monte Carlo engine (one batch)."""

    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    strategy_id: Mapped[int | None] = mapped_column(
        ForeignKey("strategies.id"), index=True
    )
    odds_american: Mapped[int | None] = mapped_column(Integer)
    win_probability: Mapped[float | None] = mapped_column(Float)
    bankroll: Mapped[float | None] = mapped_column(Float)
    bet_size: Mapped[float | None] = mapped_column(Float)
    bet_size_type: Mapped[str | None] = mapped_column(String(20))
    num_bets: Mapped[int | None] = mapped_column(Integer)
    num_simulations: Mapped[int | None] = mapped_column(Integer)
    seed: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    strategy: Mapped["Strategy | None"] = relationship(  # noqa: F821
        "Strategy", back_populates="simulation_runs"
    )
    results: Mapped[list["SimulationResult"]] = relationship(
        "SimulationResult", back_populates="simulation_run"
    )


class SimulationResult(Base):
    """Outcome of one simulation iteration within a batch."""

    __tablename__ = "simulation_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_run_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_runs.id"), index=True
    )
    run_index: Mapped[int | None] = mapped_column(Integer, index=True)
    final_bankroll: Mapped[float | None] = mapped_column(Float, index=True)
    is_profitable: Mapped[bool | None] = mapped_column(Boolean)
    max_drawdown: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    simulation_run: Mapped["SimulationRun"] = relationship(
        "SimulationRun", back_populates="results"
    )
