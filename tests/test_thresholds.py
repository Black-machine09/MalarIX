from core.config import Settings
from ml.thresholds import TriageLabel, classify_score


def test_classifies_suspected_positive() -> None:
    assert classify_score(0.8, Settings()) == TriageLabel.SUSPECTED_POSITIVE


def test_classifies_uncertain() -> None:
    assert classify_score(0.5, Settings()) == TriageLabel.LIKELY_NEGATIVE


def test_classifies_likely_negative() -> None:
    assert classify_score(0.29, Settings()) == TriageLabel.LIKELY_NEGATIVE

