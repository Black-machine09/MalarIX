from fastapi import APIRouter

from api.schemas.response import (
    Diagnosis,
    Hematology,
    HematologyParameter,
    Observation,
    PatientInfo,
    Recommendation,
    ResultResponse,
)

router = APIRouter(tags=["results"])


@router.get("/api/result/{result_id}")
def get_result(result_id: str) -> ResultResponse:
    return ResultResponse(
        id=result_id,
        status="completed",
        diagnosis=Diagnosis(
            result="positive",
            label="Positivo",
            subtitle="Malária detectada",
            species="Plasmodium falciparum",
            speciesStatus="Presente",
            stage="Trofozoíto",
            confidence=97.4,
            parasitemia=3.2,
            infectedCells=32,
            infectedCellsUnit="/µL",
        ),
        patient=PatientInfo(
            name="João Mendes Silva",
            birthDate="1988-03-14",
            gender="Masculino",
            medicalRecord="PAC-000847",
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
