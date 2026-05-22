import numpy as np
import pytest

from ml.inference import OnnxInferenceEngine


def test_score_from_single_probability_output() -> None:
    score = OnnxInferenceEngine._score_from_output(np.array([[0.87]], dtype=np.float32))

    assert score == pytest.approx(0.87)


def test_score_from_two_class_probability_output() -> None:
    score = OnnxInferenceEngine._score_from_output(np.array([[0.13, 0.87]], dtype=np.float32))

    assert score == pytest.approx(0.87)


def test_score_from_two_class_logits_output() -> None:
    score = OnnxInferenceEngine._score_from_output(np.array([[0.0, 2.0]], dtype=np.float32))

    assert score == pytest.approx(0.880797, rel=1e-5)

