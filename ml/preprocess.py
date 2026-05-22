import cv2
import numpy as np

from ml.enhance import enhance_microscope_image


def decode_image(image_bytes: bytes) -> np.ndarray | None:
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(buffer, cv2.IMREAD_COLOR)


def preprocess_image(image_bgr: np.ndarray, input_size: int) -> np.ndarray:
    """Convert an OpenCV BGR image into a model-ready CHW float tensor.

    Microscope enhancement is applied BEFORE resizing/normalization.
    """
    enhanced_bgr = enhance_microscope_image(image_bgr)

    # Model expects RGB
    image_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

    # Resize to model input_size (training used square resize)
    resized = cv2.resize(image_rgb, (input_size, input_size), interpolation=cv2.INTER_AREA)
    normalized = resized.astype(np.float32) / 255.0

    chw = np.transpose(normalized, (2, 0, 1))
    return np.expand_dims(chw, axis=0).astype(np.float32)



