from functools import lru_cache

import numpy as np

from core.config import Settings, get_settings


class InferenceError(RuntimeError):
    """Raised when model inference cannot be completed."""


class OnnxInferenceEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = None
        self.input_name = None

        if settings.demo_mode:
            return

        if not settings.model_path.exists():
            raise InferenceError(
                f"ONNX model not found at {settings.model_path}. "
                "Add the model file or set DEMO_MODE=true for local smoke tests."
            )

        try:
            import onnxruntime as ort

            self.session = ort.InferenceSession(
                str(settings.model_path),
                providers=["CPUExecutionProvider"],
            )
            self.input_name = self.session.get_inputs()[0].name
        except Exception as exc:
            raise InferenceError("failed to initialize ONNX Runtime session") from exc

    def predict_score(self, tensor: np.ndarray) -> float:
        if self.settings.demo_mode:
            return self._demo_score(tensor)

        if self.session is None or self.input_name is None:
            raise InferenceError("ONNX session is not initialized")

        try:
            outputs = self.session.run(None, {self.input_name: tensor})
            return self._score_from_output(outputs[0])
        except Exception as exc:
            raise InferenceError("ONNX inference failed") from exc

    @staticmethod
    def _score_from_output(output: np.ndarray) -> float:
        values = np.asarray(output, dtype=np.float32)

        if values.ndim == 0:
            return _coerce_probability(float(values))

        if values.ndim == 1:
            if values.size == 1:
                return _coerce_probability(float(values[0]))
            if values.size == 2:
                return float(_softmax(values)[1])

        if values.ndim >= 2:
            row = values.reshape(values.shape[0], -1)[0]
            if row.size == 1:
                return _coerce_probability(float(row[0]))
            if row.size == 2:
                if _looks_like_probability_pair(row):
                    return float(row[1])
                return float(_softmax(row)[1])

        raise InferenceError(f"unsupported model output shape: {values.shape}")

    @staticmethod
    def _demo_score(tensor: np.ndarray) -> float:
        # Explicit development-only fallback: estimates score from image darkness.
        mean_intensity = float(np.mean(tensor))
        score = 1.0 - mean_intensity
        return max(0.0, min(1.0, score))


def _coerce_probability(value: float) -> float:
    if 0.0 <= value <= 1.0:
        return value
    return float(1.0 / (1.0 + np.exp(-value)))


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _looks_like_probability_pair(values: np.ndarray) -> bool:
    return bool(
        np.all(values >= 0.0)
        and np.all(values <= 1.0)
        and np.isclose(float(np.sum(values)), 1.0, atol=1e-3)
    )


@lru_cache(maxsize=1)
def get_inference_engine() -> OnnxInferenceEngine:
    return OnnxInferenceEngine(get_settings())

