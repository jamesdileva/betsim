"""Training pipeline structure — intentionally unimplemented until a trained
model exists. The interface documents how training will slot into the
recommendation lifecycle: features -> train -> registry -> predict."""

from sqlalchemy.orm import Session


class TrainingPipeline:
    """Placeholder for future model training (Sprint 13 plan: structure only)."""

    def __init__(self, model_id: str | None = None) -> None:
        self.model_id = model_id

    def train(self, db: Session, sport: str) -> str:  # noqa: ARG002
        """Train a model and register it. Raises until training is implemented."""
        raise NotImplementedError(
            "Model training is not implemented yet. "
            "Use UserInputModel or StubModel via /api/models/predict."
        )

    def status(self) -> dict:
        return {"implemented": False, "model_id": self.model_id}
