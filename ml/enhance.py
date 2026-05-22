from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


class EnhancementError(RuntimeError):
    """Raised when microscope enhancement fails."""


def _validate_bgr(image: np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy.ndarray")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must be a BGR image with shape (H, W, 3)")
    if image.dtype != np.uint8:
        # Most OpenCV pipelines use uint8; convert defensively.
        if np.issubdtype(image.dtype, np.floating):
            image = np.clip(image, 0, 255).astype(np.uint8)
        else:
            image = image.astype(np.uint8)
    if image.shape[0] < 10 or image.shape[1] < 10:
        raise ValueError("image is too small")
    return image


def _detect_circle_mask(gray: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int, int]]:
    """Detect microscope circular ROI.

    Returns:
        mask: uint8 {0,255} mask
        circle: (x, y, r)
    """
    h, w = gray.shape[:2]

    # Pre-smooth to stabilize Hough circle detection.
    blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Hough circles are sensitive to parameters; choose conservative bounds.
    min_dim = min(h, w)
    min_r = int(0.25 * min_dim)
    max_r = int(0.55 * min_dim)

    # Attempt Hough circle detection.
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=int(0.3 * min_dim),
        param1=100,
        param2=30,
        minRadius=min_r,
        maxRadius=max_r,
    )

    if circles is not None and len(circles) > 0:
        x, y, r = circles[0][0]
        x, y, r = int(x), int(y), int(r)
    else:
        # Fallback: center-based circle.
        x, y = w // 2, h // 2
        r = int(0.45 * min_dim)

    mask = np.zeros((h, w), dtype=np.uint8)
    # Keep slightly inside the border to avoid including black microscope rim.
    r_inner = max(r - int(0.04 * r), 1)
    cv2.circle(mask, (x, y), r_inner, 255, thickness=-1)
    return mask, (x, y, r)


def _crop_nonblack_roi(image_bgr: np.ndarray, min_nonblack_ratio: float = 0.01) -> np.ndarray:
    """Crop to bounding rectangle of non-black pixels in grayscale."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Non-black threshold. Keep it low to be tolerant to warm lighting.
    # Using > 15 avoids counting near-black borders.
    nz = gray > 15

    if nz.mean() < min_nonblack_ratio:
        # If mask seems empty, do not crop.
        return image_bgr

    coords = cv2.findNonZero(nz.astype(np.uint8) * 255)
    if coords is None:
        return image_bgr

    x, y, w, h = cv2.boundingRect(coords)

    # Defensive padding inside bounds.
    pad = int(0.02 * max(w, h))
    x0 = max(x - pad, 0)
    y0 = max(y - pad, 0)
    x1 = min(x + w + pad, image_bgr.shape[1])
    y1 = min(y + h + pad, image_bgr.shape[0])

    return image_bgr[y0:y1, x0:x1]


def _apply_white_balance_gray_world(image_bgr: np.ndarray) -> np.ndarray:
    """White balance using Gray World assumption.

    Keeps morphology/color relationships stable.
    """
    b, g, r = cv2.split(image_bgr.astype(np.float32))
    # Avoid divide-by-zero
    b_mean = max(float(np.mean(b)), 1.0)
    g_mean = max(float(np.mean(g)), 1.0)
    r_mean = max(float(np.mean(r)), 1.0)

    mean_gray = (b_mean + g_mean + r_mean) / 3.0

    b_scale = mean_gray / b_mean
    g_scale = mean_gray / g_mean
    r_scale = mean_gray / r_mean

    b = np.clip(b * b_scale, 0, 255)
    g = np.clip(g * g_scale, 0, 255)
    r = np.clip(r * r_scale, 0, 255)

    return cv2.merge([b, g, r]).astype(np.uint8)


def _resize_to_800x533(image_bgr: np.ndarray) -> np.ndarray:
    """Letterbox resize to exact (800, 533) without aspect distortion."""
    target_w, target_h = 800, 533
    h, w = image_bgr.shape[:2]
    if h == 0 or w == 0:
        return image_bgr

    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    resized = cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    pad_left = (target_w - new_w) // 2
    pad_right = target_w - new_w - pad_left
    pad_top = (target_h - new_h) // 2
    pad_bottom = target_h - new_h - pad_top

    padded = cv2.copyMakeBorder(
        resized,
        pad_top,
        pad_bottom,
        pad_left,
        pad_right,
        borderType=cv2.BORDER_CONSTANT,
        value=(0, 0, 0),
    )
    return padded


def enhance_microscope_image(image: np.ndarray) -> np.ndarray:
    """Enhance a microscope blood smear image for improved ONNX inference.

    Pipeline (CPU compatible):
        input BGR image
        → detect microscope circular ROI
        → crop valid ROI / remove dark borders
        → white balance (gray-world)
        → CLAHE on LAB L channel
        → denoise
        → gentle sharpening
        → resize to 800x533 (letterbox)
        → return enhanced BGR uint8 image

    Args:
        image: Input OpenCV BGR image.

    Returns:
        Enhanced BGR image with shape (533, 800, 3).
    """

    img = _validate_bgr(image)

    try:
        # ---- Stage 1: circular ROI detection / border removal ----
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask, _circle = _detect_circle_mask(gray)

        # Apply circular mask (removes black microscope border rim).
        masked = cv2.bitwise_and(img, img, mask=mask)

        # ---- Stage 2: crop valid ROI ----
        cropped = _crop_nonblack_roi(masked)

        if cropped.shape[0] < 10 or cropped.shape[1] < 10:
            cropped = img

        # ---- Stage 3: white balance + CLAHE on L channel ----
        wb = _apply_white_balance_gray_world(cropped)

        lab = cv2.cvtColor(wb, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # CLAHE parameters required by spec
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)

        lab2 = cv2.merge([l2, a, b])
        enhanced = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)

        # ---- Stage 4: denoise ----
        # Use required OpenCV function.
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)

        # ---- Stage 5: sharpening (gentle to preserve morphology) ----
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        sharpened = cv2.filter2D(denoised, ddepth=-1, kernel=kernel)

        # Mildly blend to avoid aggressive oversharpening.
        # This keeps lesion/parasite morphology stable.
        sharpen_blend = cv2.addWeighted(denoised, 0.6, sharpened, 0.4, 0)

        # ---- Stage 6: final resize normalization to 800x533 ----
        out = _resize_to_800x533(sharpen_blend)

        # Ensure exact output shape.
        if out.shape[0] != 533 or out.shape[1] != 800:
            out = cv2.resize(out, (800, 533), interpolation=cv2.INTER_CUBIC)

        return out

    except Exception as exc:
        # Fail safe: return the original image resized/normalized.
        # This is defensive to keep the backend pipeline stable.
        try:
            fallback = _resize_to_800x533(img)
            return fallback
        except Exception:
            raise EnhancementError("Microscope enhancement failed") from exc

