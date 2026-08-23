"""ProbabilityModel ABC — the contract every predictor implements.

A model maps a feature vector to a win probability (0-1) for the HOME side
and reports its own confidence in that estimate.
"""

from abc import ABC, abstractmethod


class ProbabilityModel(ABC):
    """Swappable probability source: user input today, trained models later."""

    @abstractmethod
    def predict(self, features: dict[str, float | None]) -> float:
        """Return the predicted home-win probability, clamped to [0, 1]."""

    @abstractmethod
    def get_confidence(self, features: dict[str, float | None]) -> float:
        """Return model confidence in [0, 1] for this prediction."""

    def clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))
