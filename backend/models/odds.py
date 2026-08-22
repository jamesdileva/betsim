from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class GameOdds(Base):
    """Normalized betting odds from sportsbooks, with line-movement timestamps."""

    __tablename__ = "game_odds"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), index=True)
    sportsbook: Mapped[str | None] = mapped_column(String(50), index=True)
    market_type: Mapped[str | None] = mapped_column(String(20), index=True)
    outcome_name: Mapped[str | None] = mapped_column(String(50))
    odds_american: Mapped[int | None] = mapped_column(Integer)
    odds_decimal: Mapped[float | None] = mapped_column(Float)
    implied_probability: Mapped[float | None] = mapped_column(Float)
    is_no_vig: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    game: Mapped["Game"] = relationship("Game", back_populates="odds")  # noqa: F821


class RawOdds(Base):
    """Raw, unmodified odds from each provider before normalization."""

    __tablename__ = "raw_odds"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str | None] = mapped_column(String(50), index=True)
    provider_game_id: Mapped[str | None] = mapped_column(String(100), index=True)
    sport: Mapped[str | None] = mapped_column(String(20), index=True)
    home_team: Mapped[str | None] = mapped_column(String(100))
    away_team: Mapped[str | None] = mapped_column(String(100))
    market_type: Mapped[str | None] = mapped_column(String(20))
    outcome_name: Mapped[str | None] = mapped_column(String(50))
    odds_american: Mapped[int | None] = mapped_column(Integer)
    odds_decimal: Mapped[float | None] = mapped_column(Float)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    raw_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
