from dataclasses import dataclass

import cv2
import numpy as np

from core.config import Settings


@dataclass(frozen=True)
class QualityResult:
    accepted: bool
    reason: str | None
    blur_score: float
    contrast_score: float
    brightness: float


def validate_image_quality(image_bgr: np.ndarray, settings: Settings) -> QualityResult:
    height, width = image_bgr.shape[:2]
    if width < settings.min_width or height < settings.min_height:
        return QualityResult(False, "image_too_small", 0.0, 0.0, 0.0)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    contrast_score = float(np.std(gray))
    brightness = float(np.mean(gray))

    # Enhancement improves contrast/brightness; to avoid rejecting potentially usable microscopy,
    # keep this gate relatively permissive.
    if blur_score < settings.blur_threshold:
        return QualityResult(False, "blur_score_too_low", blur_score, contrast_score, brightness)

    if contrast_score < settings.min_contrast:
        return QualityResult(False, "contrast_too_low", blur_score, contrast_score, brightness)

    if brightness < settings.min_brightness:
        return QualityResult(False, "image_too_dark", blur_score, contrast_score, brightness)

    if brightness > settings.max_brightness:
        return QualityResult(False, "image_too_bright", blur_score, contrast_score, brightness)


    return QualityResult(True, None, blur_score, contrast_score, brightness)

