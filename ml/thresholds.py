from enum import Enum

from core.config import Settings


class TriageLabel(str, Enum):
    SUSPECTED_POSITIVE = "suspected_positive"
    UNCERTAIN = "uncertain"
    LIKELY_NEGATIVE = "likely_negative"


def classify_score(score: float, settings: Settings) -> TriageLabel:
    """Map score to labels.

    This version removes the "uncertain" band: everything below positive_threshold
    is treated as likely_negative.
    """
    if score >= settings.positive_threshold:
        return TriageLabel.SUSPECTED_POSITIVE
    return TriageLabel.LIKELY_NEGATIVE


