from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class SystemPlayResult(Base):
    """System Plays Engine output: stated probability vs. simulated win rate."""

    __tablename__ = "system_play_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("simulation_runs.id"), index=True
    )
    stated_probability: Mapped[float | None] = mapped_column(Float)
    actual_win_rate: Mapped[float | None] = mapped_column(Float)
    calibration_error: Mapped[float | None] = mapped_column(Float)
    calibration_status: Mapped[str | None] = mapped_column(String(50), index=True)
    confidence_interval_low: Mapped[float | None] = mapped_column(Float)
    confidence_interval_high: Mapped[float | None] = mapped_column(Float)
    recommendation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    simulation_run: Mapped["SimulationRun | None"] = relationship(  # noqa: F821
        "SimulationRun"
    )
