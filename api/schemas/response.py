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

