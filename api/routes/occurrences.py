from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["occurrences"])



@router.get("/occurrences")
def occurrences():
    """Stub para lista de ocorrências.

    Retorna dados de exemplo para que o frontend pare de receber 404.
    """

    return {
        "status": "ok",
        "items": [
            {
                "id": "occ_001",
                "created_at": "2026-05-16T10:12:30Z",
                "label": "suspected_positive",
                "confidence": 0.91,
            },
            {
                "id": "occ_002",
                "created_at": "2026-05-16T10:18:02Z",
                "label": "uncertain",
                "confidence": 0.54,
            },
            {
                "id": "occ_003",
                "created_at": "2026-05-16T10:22:49Z",
                "label": "likely_negative",
                "confidence": 0.12,
            },
        ],
        "limit": 20,
        "offset": 0,
        "total": 3,
    }

