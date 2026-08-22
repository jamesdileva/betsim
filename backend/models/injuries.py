from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Injury(Base):
    """Normalized injury data linked to teams; drives ML feature engineering."""

    __tablename__ = "injuries"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_name: Mapped[str | None] = mapped_column(String(100), index=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), index=True)
    sport: Mapped[str | None] = mapped_column(String(20), index=True)
    injury_type: Mapped[str | None] = mapped_column(String(50))
    severity: Mapped[str | None] = mapped_column(String(20), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    reported_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team: Mapped["Team | None"] = relationship("Team", back_populates="injuries")  # noqa: F821


class RawInjury(Base):
    """Raw injury reports from data providers before normalization."""

    __tablename__ = "raw_injuries"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str | None] = mapped_column(String(50), index=True)
    player_name: Mapped[str | None] = mapped_column(String(100), index=True)
    team_name: Mapped[str | None] = mapped_column(String(100), index=True)
    sport: Mapped[str | None] = mapped_column(String(20), index=True)
    injury_type: Mapped[str | None] = mapped_column(String(50))
    severity: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    reported_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    raw_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
