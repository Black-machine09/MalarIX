from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    images_processed: int = Field(ge=1)
    images_rejected: int = Field(ge=0)
    model_version: str


class ErrorResponse(BaseModel):
    error: str
    message: str


# ─── Auth ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str
    remember: bool = False


class AuthUser(BaseModel):
    name: str
    specialty: str
    avatar: str | None = None


class LoginResponse(BaseModel):
    token: str
    user: AuthUser


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    confirmPassword: str
    acceptTerms: bool = False


# ─── Patient / Analysis ─────────────────────────────────────────────────

class PatientData(BaseModel):
    name: str
    birthDate: str
    gender: str
    medicalRecord: str


class AnalyzeRequest(BaseModel):
    image: str
    patient: PatientData


# ─── Hematology ─────────────────────────────────────────────────────────

class HematologyParameter(BaseModel):
    value: float
    unit: str
    refMin: float
    refMax: float
    status: str  # "low" | "high" | "normal"


class Hematology(BaseModel):
    hemoglobin: HematologyParameter
    hematocrit: HematologyParameter
    erythrocytes: HematologyParameter
    leukocytes: HematologyParameter
    platelets: HematologyParameter
    mcv: HematologyParameter
    mch: HematologyParameter
    neutrophils: HematologyParameter
    lymphocytes: HematologyParameter


# ─── Observations & Recommendations ─────────────────────────────────────

class Observation(BaseModel):
    severity: str  # "critical" | "warning" | "info"
    text: str


class Recommendation(BaseModel):
    icon: str
    title: str
    description: str


# ─── Diagnosis ──────────────────────────────────────────────────────────

class Diagnosis(BaseModel):
    result: str
    label: str
    subtitle: str
    species: str
    speciesStatus: str
    stage: str
    confidence: float
    parasitemia: float
    infectedCells: int
    infectedCellsUnit: str


# ─── Patient Info (result) ──────────────────────────────────────────────

class PatientInfo(BaseModel):
    name: str
    birthDate: str
    gender: str
    medicalRecord: str
    examDate: str
    physician: str


# ─── Full Result ────────────────────────────────────────────────────────

class ResultResponse(BaseModel):
    id: str
    status: str
    diagnosis: Diagnosis
    patient: PatientInfo
    hematology: Hematology
    observations: list[Observation]
    recommendations: list[Recommendation]
    imageUrl: str


# ─── Upload History ─────────────────────────────────────────────────────

class UploadHistoryItem(BaseModel):
    id: str
    patientName: str
    examDate: str
    result: str
    confidence: float
    species: str


class UploadHistoryResponse(BaseModel):
    items: list[UploadHistoryItem]
