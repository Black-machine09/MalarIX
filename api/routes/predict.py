from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from api.schemas.response import PredictionResponse
from core.config import get_settings
from ml.aggregation import mean_score
from ml.inference import InferenceError, get_inference_engine
from ml.preprocess import decode_image, preprocess_image
from ml.quality import validate_image_quality
from ml.thresholds import classify_score

router = APIRouter(prefix="/api/v1", tags=["prediction"])


def api_error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message},
    )


@router.post("/predict-batch", response_model=PredictionResponse)
async def predict_batch(files: list[UploadFile] = File(default_factory=list)):
    settings = get_settings()

    if not files:
        return api_error(
            400,
            "no_images_provided",
            "At least one image file is required.",
        )

    if len(files) > settings.max_batch_images:
        return api_error(
            400,
            "too_many_images",
            f"The request exceeds the maximum batch size of {settings.max_batch_images}.",
        )

    try:
        engine = get_inference_engine()
    except InferenceError as exc:
        return api_error(
            500,
            "model_not_loaded",
            str(exc),
        )

    scores: list[float] = []
    rejected = 0
    decode_failures = 0
    quality_failures = 0
    quality_reasons: dict[str, int] = {}

    for upload in files:
        if upload.content_type not in settings.accepted_mime_types:
            return api_error(
                415,
                "unsupported_media_type",
                "Only JPG and PNG images are supported.",
            )

        image_bytes = await upload.read()
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(image_bytes) > max_bytes:
            return api_error(
                413,
                "file_too_large",
                "One or more uploaded files exceed the maximum allowed size.",
            )

        image = decode_image(image_bytes)
        if image is None:
            decode_failures += 1
            rejected += 1
            continue

        # Quality gate BEFORE enhancement.
        # Observação: enhancement pode recuperar imagens com baixo contraste/temperatura.
        quality = validate_image_quality(image, settings)

        # Preprocess (enhancement acontece dentro de preprocess_image).
        tensor = preprocess_image(image, settings.input_size)

        if not quality.accepted:
            quality_failures += 1
            rejected += 1
            if quality.reason:
                quality_reasons[quality.reason] = quality_reasons.get(quality.reason, 0) + 1

        try:
            scores.append(engine.predict_score(tensor))
        except InferenceError:
            return api_error(
                500,
                "inference_failed",
                "The model could not process the request.",
            )

    if not scores:
        # Se tudo falhar no decode, isso é diferente de falha na validação de qualidade.
        if decode_failures == len(files) and len(files) > 0:
            return api_error(
                422,
                "image_decode_failed",
                "OpenCV não conseguiu decodificar as imagens enviadas. Verifique se o arquivo não está corrompido e se o multipart usa o campo 'files' corretamente.",
            )

        # Caso contrário, é provável que seja falha de qualidade (ou ambos).
        reasons_preview = (
            ", ".join(f"{k}={v}" for k, v in list(quality_reasons.items())[:5])
            if quality_reasons
            else "unknown"
        )
        return api_error(
            422,
            "image_quality_insufficient",
            f"Nenhuma imagem passou nos critérios mínimos de qualidade. Razões detectadas: {reasons_preview}. Ajuste os thresholds em core/config.py (blur/contrast/brightness).",
        )



    final_score = mean_score(scores)

    return {
        "label": classify_score(final_score, settings).value,
        "confidence": round(final_score, 4),
        "images_processed": len(scores),
        "images_rejected": rejected,
        "model_version": settings.model_version,
    }
