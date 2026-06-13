from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.database import create_exam, create_patient
from core.database import init_db  # noqa: F401

router = APIRouter(prefix="/api/v1", tags=["exams"])


class ExamCreateRequest(BaseModel):
    patient_name: str = Field(min_length=1, max_length=200)
    birth_date: str = Field(min_length=4, max_length=20)
    gender: str = Field(min_length=1, max_length=50)
    exam_date: str = Field(min_length=4, max_length=20)


def api_error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "message": message})


@router.post("/exams")
def create_exam_endpoint(payload: ExamCreateRequest):
    # Keep it flexible: birth_date/exam_date are stored as strings (ISO recommended).
    patient_id = create_patient(payload.patient_name, payload.birth_date, payload.gender)
    exam_id = create_exam(patient_id, payload.exam_date)
    return {"status": "ok", "exam_id": exam_id}

