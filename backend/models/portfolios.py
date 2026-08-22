from datetime import date as dt_date
from datetime import datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Portfolio(Base):
    """Portfolio construction result: the recommended set of bets for a day."""

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt_date | None] = mapped_column(Date, index=True)
    total_risk: Mapped[float | None] = mapped_column(Float)
    expected_roi: Mapped[float | None] = mapped_column(Float)
    kelly_exposure: Mapped[float | None] = mapped_column(Float)
    model_id: Mapped[str | None] = mapped_column(ForeignKey("ml_models.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list["PortfolioItem"]] = relationship(
        "PortfolioItem", back_populates="portfolio"
    )
    model: Mapped["MlModel | None"] = relationship("MlModel")  # noqa: F821


class PortfolioItem(Base):
    """An individual bet within a portfolio."""

    __tablename__ = "portfolio_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"), index=True)
    game_id: Mapped[str | None] = mapped_column(ForeignKey("games.id"), index=True)
    model_id: Mapped[str | None] = mapped_column(ForeignKey("ml_models.id"))
    confidence_level: Mapped[str | None] = mapped_column(String(20), index=True)
    bet_type: Mapped[str | None] = mapped_column(String(20))
    stake: Mapped[float | None] = mapped_column(Float)
    predicted_probability: Mapped[float | None] = mapped_column(Float)
    ev: Mapped[float | None] = mapped_column(Float)
    recommendation_stars: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="items"
    )
    game: Mapped["Game | None"] = relationship("Game")  # noqa: F821
    model: Mapped["MlModel | None"] = relationship("MlModel")  # noqa: F821
