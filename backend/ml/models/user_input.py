"""UserInputModel: the MVP "model" — the user IS the model."""

from ml.models.base import ProbabilityModel


class UserInputModel(ProbabilityModel):
    """Wraps a user-supplied probability; confidence is the user's stated certainty."""

    def __init__(self, probability: float, confidence: float = 0.5) -> None:
        self.probability = self.clamp(probability)
        self.confidence = self.clamp(confidence)

    def predict(self, features: dict[str, float | None]) -> float:
        return self.probability

    def get_confidence(self, features: dict[str, float | None]) -> float:
        return self.confidence
