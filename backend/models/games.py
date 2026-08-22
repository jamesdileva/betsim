from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Game(Base):
    """Every historical and future game across all sports."""

    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    sport: Mapped[str] = mapped_column(String(20), index=True)
    league: Mapped[str | None] = mapped_column(String(50))
    home_team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"), index=True
    )
    away_team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"), index=True
    )
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    game_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    status: Mapped[str | None] = mapped_column(String(20), index=True, default="scheduled")
    season: Mapped[str | None] = mapped_column(String(10), index=True)
    week: Mapped[int | None] = mapped_column(Integer)
    venue: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    home_team: Mapped["Team | None"] = relationship(  # noqa: F821
        "Team", foreign_keys=[home_team_id], back_populates="home_games"
    )
    away_team: Mapped["Team | None"] = relationship(  # noqa: F821
        "Team", foreign_keys=[away_team_id], back_populates="away_games"
    )
    odds: Mapped[list["GameOdds"]] = relationship(  # noqa: F821
        "GameOdds", back_populates="game"
    )
    predictions: Mapped[list["ModelPrediction"]] = relationship(  # noqa: F821
        "ModelPrediction", back_populates="game"
    )
    backtest_results: Mapped[list["BacktestResult"]] = relationship(  # noqa: F821
        "BacktestResult", back_populates="game"
    )
