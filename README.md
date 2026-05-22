# Malaria Triage AI - MVP

This workspace contains the MVP v1 project for **Malaria Triage AI**, a computer vision triage-support system for assisted malaria screening from microscope blood smear images.

The system is intended for research, education, and proof-of-concept screening workflows only. It is **not** a clinical diagnostic device.

## Project Files

| Path | Purpose |
| --- | --- |
| `app.py` | FastAPI application entrypoint |
| `api/routes/predict.py` | `/api/v1/predict-batch` endpoint |
| `ml/inference.py` | ONNX Runtime inference engine |
| `ml/preprocess.py` | OpenCV image decoding and tensor preprocessing |
| `ml/quality.py` | Blur, contrast, brightness, and size validation |
| `ml/thresholds.py` | Triage classification thresholds |
| `model/malaria_resnet18.onnx` | Expected ONNX model location |
| `docs/` | Technical documentation package |

## Documentation Package

| File | Purpose |
| --- | --- |
| [docs/technical-documentation-mvp-v1.md](docs/technical-documentation-mvp-v1.md) | Full system architecture, ML pipeline, deployment guidance, risks, and roadmap |
| [docs/api-contract.md](docs/api-contract.md) | API endpoint contract, request/response formats, validation rules, and errors |
| [docs/model-card-mvp-v1.md](docs/model-card-mvp-v1.md) | MVP model card with intended use, limitations, evaluation priorities, and safety notes |
| [docs/mvp-delivery-checklist.md](docs/mvp-delivery-checklist.md) | Practical checklist for same-day MVP completion and handoff |

## ONNX Model

Place the trained model here:

```text
model/malaria_resnet18.onnx
```

The inference engine supports common binary classifier outputs:

- one sigmoid probability, for example shape `[1, 1]`
- two-class probabilities, for example shape `[1, 2]`
- two-class logits, converted with softmax

For real inference, keep:

```text
DEMO_MODE=false
```

For local smoke tests without a model file, set:

```text
DEMO_MODE=true
```

Also verify that the expected ONNX model path exists at:

```text
model/malaria_resnet18.onnx
```


The demo mode is development-only and does not represent medical or model performance.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

Prediction request:

```bash
curl -X POST http://localhost:8000/api/v1/predict-batch \
  -F "files=@img1.jpg" \
  -F "files=@img2.jpg" \
  -F "files=@img3.jpg"
```

## Docker

```bash
docker build -t malaria-triage-ai .
docker run --rm -p 8000:8000 --env-file .env malaria-triage-ai
```

## MVP Summary

Malaria Triage AI uses a lightweight ONNX-exported deep learning model to analyze microscope blood smear images and return a triage-oriented classification:

- `suspected_positive`
- `uncertain`
- `likely_negative`

The MVP emphasizes high sensitivity, quality validation, multi-image aggregation, CPU-compatible inference, and mandatory human laboratory review.

## Recommended Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Inference | ONNX Runtime |
| Image Processing | OpenCV |
| Training | PyTorch |
| Metrics | Scikit-learn |
| Deployment | Docker, Uvicorn, Nginx |

## Regulatory Notice

This project is an AI-assisted triage prototype. It must not be used as a standalone medical diagnostic system. Human laboratory review remains mandatory for all results.
