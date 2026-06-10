from fastapi import APIRouter

from api.schemas.response import UploadHistoryItem, UploadHistoryResponse

router = APIRouter(tags=["uploads"])


@router.get("/api/uploads")
def uploads() -> UploadHistoryResponse:
    return UploadHistoryResponse(
        items=[
            UploadHistoryItem(
                id="res-001",
                patientName="João Mendes Silva",
                examDate="2025-07-23T14:32:00",
                result="positive",
                confidence=97.4,
                species="Plasmodium falciparum",
            ),
        ],
    )
