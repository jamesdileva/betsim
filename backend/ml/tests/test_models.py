import pytest

from ml.models.base import ProbabilityModel
from ml.models.stub import StubModel
from ml.models.user_input import UserInputModel
from ml.pipeline import TrainingPipeline


class TestUserInputModel:
    def test_predict_returns_exact_user_probability(self) -> None:
        model = UserInputModel(probability=0.62)
        assert model.predict({}) == pytest.approx(0.62)

    def test_confidence_is_configurable(self) -> None:
        assert UserInputModel(0.6).get_confidence({}) == pytest.approx(0.5)
        assert UserInputModel(0.6, confidence=0.9).get_confidence({}) == pytest.approx(0.9)

    def test_probability_clamped(self) -> None:
        assert UserInputModel(1.5).predict({}) == 1.0
        assert UserInputModel(-0.5).predict({}) == 0.0

    def test_implements_abc(self) -> None:
        assert isinstance(UserInputModel(0.5), ProbabilityModel)


class TestStubModel:
    def test_predict_within_bounds(self) -> None:
        for p in (0.0, 0.3, 0.5, 0.99):
            value = StubModel(p).predict({"anything": None})
            assert 0.0 <= value <= 1.0
            assert value == pytest.approx(p)

    def test_default_is_neutral(self) -> None:
        assert StubModel().predict({}) == pytest.approx(0.5)
        assert StubModel().get_confidence({}) == pytest.approx(0.5)


class TestTrainingPipeline:
    def test_train_raises_not_implemented(self) -> None:
        pipeline = TrainingPipeline(model_id="m1")
        with pytest.raises(NotImplementedError, match="not implemented"):
            pipeline.train(db=None, sport="nfl")  # type: ignore[arg-type]

    def test_status_reports_placeholder_state(self) -> None:
        assert TrainingPipeline("m1").status() == {"implemented": False, "model_id": "m1"}
