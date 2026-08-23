"""StubModel: deterministic placeholder for tests and pipeline plumbing."""

from ml.models.base import ProbabilityModel


class StubModel(ProbabilityModel):
    """Returns a fixed probability with fixed confidence — never varies."""

    def __init__(self, probability: float = 0.5, confidence: float = 0.5) -> None:
        self.probability = self.clamp(probability)
        self.confidence = self.clamp(confidence)

    def predict(self, features: dict[str, float | None]) -> float:
        return self.probability

    def get_confidence(self, features: dict[str, float | None]) -> float:
        return self.confidence
