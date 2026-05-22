import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _csv_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None:
        return default
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    return items or default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Malaria Triage AI")
    api_base_path: str = os.getenv("API_BASE_PATH", "/api/v1")

    model_path: Path = Path(os.getenv("MODEL_PATH", "model/malaria_resnet18.onnx"))
    model_version: str = os.getenv("MODEL_VERSION", "resnet18_v1")
    demo_mode: bool = _bool_env("DEMO_MODE", False)

    input_size: int = int(os.getenv("INPUT_SIZE", "224"))
    positive_threshold: float = float(os.getenv("POSITIVE_THRESHOLD", "0.80"))
    negative_threshold: float = float(os.getenv("NEGATIVE_THRESHOLD", "0.30"))

    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    max_batch_images: int = int(os.getenv("MAX_BATCH_IMAGES", "20"))
    accepted_mime_types: tuple[str, ...] = _csv_env(
        "ACCEPTED_MIME_TYPES",
        ("image/jpeg", "image/png"),
    )

    # Allow smaller input images (frontend currently sends smaller resolutions).
    # Can be overridden via env vars.
    min_width: int = int(os.getenv("MIN_IMAGE_WIDTH", "64"))
    min_height: int = int(os.getenv("MIN_IMAGE_HEIGHT", "64"))

    # Quality validation thresholds.
    # These defaults are intentionally permissive to avoid rejecting valid microscopy images.
    blur_threshold: float = float(os.getenv("BLUR_THRESHOLD", "20"))
    min_contrast: float = float(os.getenv("MIN_CONTRAST", "5"))
    min_brightness: float = float(os.getenv("MIN_BRIGHTNESS", "5"))
    max_brightness: float = float(os.getenv("MAX_BRIGHTNESS", "245"))

    # Optional: enhance images using xAI/Grok before quality validation + inference.

    grok_enhance_enabled: bool = _bool_env("GROK_ENHANCE_ENABLED", False)
    grok_api_key: str | None = os.getenv("GROK_API_KEY")
    grok_model: str = os.getenv("GROK_MODEL", "grok-imagine-image-quality")

    # Endpoint for image edits.
    grok_image_edits_url: str = os.getenv(
        "GROK_IMAGE_EDITS_URL",
        "https://api.x.ai/v1/images/edits",
    )

    grok_timeout_sec: float = float(os.getenv("GROK_TIMEOUT_SEC", "60"))
    grok_enhance_prompt: str | None = os.getenv("GROK_ENHANCE_PROMPT")



@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

