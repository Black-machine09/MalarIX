def mean_score(scores: list[float]) -> float:
    if not scores:
        raise ValueError("at least one score is required")
    return float(sum(scores) / len(scores))

