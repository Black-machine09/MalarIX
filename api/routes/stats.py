from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])



@router.get("/dashboard")
def dashboard():
    """Stub para o dashboard.

    O frontend está tentando chamar endpoints como /stats/dashboard e /occurrences.
    Este retorno é apenas um exemplo para remover 404 e destravar a UI.
    """

    return {
        "status": "ok",
        "summary": {
            "total_occurrences": 42,
            "suspected_positive": 17,
            "uncertain": 9,
            "likely_negative": 16,
        },
        "time_series": [
            {"day": "2026-05-14", "suspected_positive": 2, "uncertain": 1, "likely_negative": 3},
            {"day": "2026-05-15", "suspected_positive": 4, "uncertain": 2, "likely_negative": 3},
            {"day": "2026-05-16", "suspected_positive": 1, "uncertain": 3, "likely_negative": 6},
        ],
        "model_version": "resnet18_v1",
    }

