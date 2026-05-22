import pytest

from ml.aggregation import mean_score


def test_mean_score_returns_average() -> None:
    assert mean_score([0.2, 0.4, 0.6]) == pytest.approx(0.4)


def test_mean_score_rejects_empty_list() -> None:
    with pytest.raises(ValueError):
        mean_score([])

