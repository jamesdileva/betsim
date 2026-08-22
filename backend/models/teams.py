from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Team(Base):
    """Master list of sports teams across all leagues."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    sport: Mapped[str] = mapped_column(String(20), index=True)
    league: Mapped[str | None] = mapped_column(String(50), index=True)
    city: Mapped[str | None] = mapped_column(String(50))
    abbreviation: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    home_games: Mapped[list["Game"]] = relationship(  # noqa: F821
        "Game", foreign_keys="Game.home_team_id", back_populates="home_team"
    )
    away_games: Mapped[list["Game"]] = relationship(  # noqa: F821
        "Game", foreign_keys="Game.away_team_id", back_populates="away_team"
    )
    injuries: Mapped[list["Injury"]] = relationship(  # noqa: F821
        "Injury", back_populates="team"
    )
