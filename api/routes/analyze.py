from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from api.schemas.response import (
    Diagnosis,
    Hematology,
    HematologyParameter,
    Observation,
    PatientInfo,
    PatientData,
    Recommendation,
    ResultResponse,
)
from core.config import get_settings
from ml.aggregation import mean_score
from ml.inference import InferenceError, get_inference_engine
from ml.preprocess import decode_image, preprocess_image
from ml.quality import validate_image_quality
from ml.thresholds import classify_score

router = APIRouter(tags=["analyze"])


def api_error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message},
    )


@router.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_birth_date: str = Form(...),
    patient_gender: str = Form(...),
    patient_medical_record: str = Form(...),
):
    settings = get_settings()

    if image.content_type not in settings.accepted_mime_types:
        return api_error(
            415,
            "unsupported_media_type",
            "Only JPG and PNG images are supported.",
        )

    image_bytes = await image.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(image_bytes) > max_bytes:
        return api_error(
            413,
            "file_too_large",
            "O arquivo excede o tamanho máximo permitido.",
        )

    decoded = decode_image(image_bytes)
    if decoded is None:
        return api_error(
            422,
            "image_decode_failed",
            "Não foi possível decodificar a imagem.",
        )

    quality = validate_image_quality(decoded, settings)
    tensor = preprocess_image(decoded, settings.input_size)

    if not quality.accepted:
        return api_error(
            422,
            "image_quality_insufficient",
            f"Qualidade insuficiente: {quality.reason}.",
        )

    try:
        engine = get_inference_engine()
        score = engine.predict_score(tensor)
    except InferenceError as exc:
        return api_error(
            500,
            "inference_failed",
            str(exc),
        )

    label = classify_score(score, settings)
    confidence = round(score, 4)
    is_positive = label.value == "suspected_positive"

    return ResultResponse(
        id="res-001",
        status="completed",
        diagnosis=Diagnosis(
            result="positive" if is_positive else "negative",
            label="Positivo" if is_positive else "Negativo",
            subtitle="Malária detectada" if is_positive else "Sem indícios de malária",
            species="Plasmodium falciparum" if is_positive else "N/A",
            speciesStatus="Presente" if is_positive else "Ausente",
            stage="Trofozoíto" if is_positive else "N/A",
            confidence=round(confidence * 100, 1),
            parasitemia=3.2 if is_positive else 0.0,
            infectedCells=32 if is_positive else 0,
            infectedCellsUnit="/µL",
        ),
        patient=PatientInfo(
            name=patient_name,
            birthDate=patient_birth_date,
            gender=patient_gender,
            medicalRecord=patient_medical_record,
            examDate="2025-07-23T14:32:00",
            physician="Dr. Ana Costa",
        ),
        hematology=Hematology(
            hemoglobin=HematologyParameter(value=9.2, unit="g/dL", refMin=12.0, refMax=16.0, status="low"),
            hematocrit=HematologyParameter(value=28, unit="%", refMin=36, refMax=48, status="low"),
            erythrocytes=HematologyParameter(value=3.1, unit="M/µL", refMin=3.8, refMax=5.2, status="low"),
            leukocytes=HematologyParameter(value=11.4, unit="K/µL", refMin=4.5, refMax=11.0, status="high"),
            platelets=HematologyParameter(value=82, unit="K/µL", refMin=150, refMax=400, status="low"),
            mcv=HematologyParameter(value=74, unit="fL", refMin=80, refMax=100, status="low"),
            mch=HematologyParameter(value=22.1, unit="pg", refMin=27, refMax=33, status="low"),
            neutrophils=HematologyParameter(value=78, unit="%", refMin=50, refMax=70, status="high"),
            lymphocytes=HematologyParameter(value=14, unit="%", refMin=20, refMax=40, status="low"),
        ),
        observations=[
            Observation(
                severity="critical",
                text="Anemia hemolítica severa: hemoglobina e hematócrito criticamente baixos — compatíveis com destruição eritrocitária por Plasmodium falciparum.",
            ),
            Observation(
                severity="critical",
                text="Trombocitopenia significativa (82 K/µL): risco aumentado de sangramento — monitoramento intensivo recomendado.",
            ),
            Observation(
                severity="warning",
                text="Leucocitose com neutrofilia relativa: resposta inflamatória ativa. Descartar infecção bacteriana secundária.",
            ),
            Observation(
                severity="info",
                text="Morfologia eritrocitária compatível com microcitose e hipocromia — possivelmente anemia ferropriva subjacente.",
            ),
        ],
        recommendations=[
            Recommendation(
                icon="pill",
                title="Artemeter + Lumefantrina",
                description="Protocolo de 1ª linha para P. falciparum",
            ),
            Recommendation(
                icon="thermometer",
                title="Monitorar sinais vitais",
                description="A cada 4h nas primeiras 24 horas",
            ),
            Recommendation(
                icon="droplets",
                title="Hidratação venosa",
                description="Soro fisiológico 0.9% — 1000mL/6h",
            ),
            Recommendation(
                icon="calendar-check",
                title="Retorno em 48h",
                description="Hemograma de controle e parasitemia",
            ),
        ],
        imageUrl="https://storage.googleapis.com/banani-generated-images/generated-images/02df3e24-91db-444c-b6e4-c02e793cd352.jpg",
    )
