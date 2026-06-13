from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])



@router.get("/dashboard")
def dashboard():
    """Dashboard real calculado a partir do SQLite."""

    from core.database import dashboard_by_day
    from core.config import get_settings

    settings = get_settings()
    data = dashboard_by_day()
    return {
        "status": "ok",
        "summary": data["summary"],
        "time_series": data["time_series"],
        "model_version": settings.model_version,
    }


