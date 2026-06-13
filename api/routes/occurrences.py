from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["occurrences"])



@router.get("/occurrences")
def occurrences(limit: int = 20, offset: int = 0):
    """Lista ocorrências (triagens) armazenadas no SQLite."""

    from core.database import list_triages

    total, items = list_triages(limit=limit, offset=offset)
    return {
        "status": "ok",
        "items": items,
        "limit": limit,
        "offset": offset,
        "total": total,
    }


