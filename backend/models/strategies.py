from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Strategy(Base):
    """User-saved betting strategy: a complete set of simulation parameters."""

    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    odds_american: Mapped[int | None] = mapped_column(Integer)
    win_probability: Mapped[float | None] = mapped_column(Float)
    bankroll: Mapped[float | None] = mapped_column(Float)
    bet_size: Mapped[float | None] = mapped_column(Float)
    bet_size_type: Mapped[str | None] = mapped_column(String(20), default="flat")
    num_bets: Mapped[int | None] = mapped_column(Integer)
    num_simulations: Mapped[int | None] = mapped_column(Integer, default=5000)
    strategy_type: Mapped[str | None] = mapped_column(String(20), default="single")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    simulation_runs: Mapped[list["SimulationRun"]] = relationship(  # noqa: F821
        "SimulationRun", back_populates="strategy"
    )
