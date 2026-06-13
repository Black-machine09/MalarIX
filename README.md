# Malaria Triage AI - MVP

Este workspace contém o MVP v1 do **Malaria Triage AI**, um sistema de apoio à triagem de malária por visão computacional a partir de imagens de esfregaço de sangue ao microscópio.

> **Aviso regulatório**: o sistema é destinado a pesquisa, educação e provas de conceito. **Não é um dispositivo diagnóstico clínico**.

---

## Endpoints da API (tudo que o sistema expõe)

**Base URL**: `http://localhost:8000`

### `GET /health`
Health check.

**Resposta 200**
```json
{ "status": "ok" }
```

---

### `POST /api/v1/exams`
Cria um paciente e registra um exame, retornando um `exam_id`.

**Request**: `application/json`

**Body**
```json
{
  "patient_name": "Maria Silva",
  "birth_date": "1990-01-01",
  "gender": "F",
  "exam_date": "2026-06-12"
}
```

**Resposta 200**
```json
{ "status": "ok", "exam_id": "<string>" }
```

---

### `POST /api/v1/predict-batch`
Envia 1 a N imagens (JPEG/PNG) para inferência e triagem em lote.

**Request**: `multipart/form-data`

- Query param: `exam_id`
- Body (form-data):
  - `files` (File) — repita a mesma key para cada imagem

**URL**
`http://localhost:8000/api/v1/predict-batch?exam_id=<SEU_EXAM_ID>`

**Resposta 200**
```json
{
  "label": "suspected_positive",
  "confidence": 0.8732,
  "images_processed": 3,
  "images_rejected": 0,
  "model_version": "resnet18_v1",
  "triage_id": "<string>"
}
```

**Limites/configurações (via env)**
- `MAX_BATCH_IMAGES` (default **20**)
- `MAX_UPLOAD_MB` (default **10**)
- `ACCEPTED_MIME_TYPES` (default `image/jpeg,image/png`)

**Erros comuns**
- `400 no_images_provided`: sem `files`
- `400 exam_id_required`: sem `exam_id`
- `400 too_many_images`: mais que `MAX_BATCH_IMAGES`
- `413 file_too_large`: imagem > `MAX_UPLOAD_MB`
- `415 unsupported_media_type`: MIME não aceito
- `422 image_decode_failed`: OpenCV não decodificou todas as imagens
- `422 image_quality_insufficient`: nenhuma passou no gate mínimo de qualidade
- `500 model_not_loaded`: ONNX não carregou (quando `DEMO_MODE=false`)

**Exemplo (curl)**
```bash
curl -X POST "http://localhost:8000/api/v1/predict-batch?exam_id=SEU_EXAM_ID" \
  -F "files=@img1.jpg" \
  -F "files=@img2.jpg" \
  -F "files=@img3.jpg"
```

---

### `GET /api/v1/occurrences`
Lista triagens armazenadas no SQLite (paginado).

**Query params**
- `limit` (default 20)
- `offset` (default 0)

**Resposta 200 (estrutura)**
```json
{
  "status": "ok",
  "items": [
    {
      "id": "<triage_id>",
      "created_at": "<iso>",
      "label": "suspected_positive|uncertain|likely_negative",
      "confidence": 0.91
    }
  ],
  "limit": 20,
  "offset": 0,
  "total": 3
}
```

---

### `GET /api/v1/stats/dashboard`
Dashboard por dia calculado a partir do SQLite.

**Resposta 200 (estrutura)**
```json
{
  "status": "ok",
  "summary": {
    "total_occurrences": 42,
    "suspected_positive": 17,
    "uncertain": 9,
    "likely_negative": 16
  },
  "time_series": [
    {
      "day": "2026-05-14",
      "suspected_positive": 2,
      "uncertain": 1,
      "likely_negative": 3
    }
  ],
  "model_version": "resnet18_v1"
}
```

---

## Testes manuais no Postman (passo a passo)

### 1) Health
- Method: `GET`
- URL: `http://localhost:8000/health`

### 2) Create Exam
- Method: `POST`
- URL: `http://localhost:8000/api/v1/exams`
- Body: **raw JSON**

### 3) Predict Batch
- Method: `POST`
- URL: `http://localhost:8000/api/v1/predict-batch?exam_id=<EXAM_ID>`
- Body: **form-data**
  - `files` (tipo **File**) — adicione uma linha por arquivo.

---

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

> Observação sobre `DEMO_MODE`: se `DEMO_MODE=false` e o arquivo `model/malaria_resnet18.onnx` não existir, o servidor falha no startup.

---

## Docker

```bash
docker build -t malaria-triage-ai .
docker run --rm -p 8000:8000 --env-file .env malaria-triage-ai
```

---

## Modelo ONNX e modo demo

- Modelo esperado: `model/malaria_resnet18.onnx`
- Para testar sem o modelo real: `DEMO_MODE=true`
- Para inferência real: `DEMO_MODE=false`

---

## MVP Summary

O Malaria Triage AI usa um modelo leve em ONNX para analisar imagens de lâminas e retornar uma classificação orientada à triagem:

- `suspected_positive`
- `uncertain`
- `likely_negative`

---

## Stack recomendada

| Camada | Tecnologia |
| --- | --- |
| API | FastAPI |
| Inference | ONNX Runtime |
| Image Processing | OpenCV |
| Treinamento | PyTorch |
| Métricas | Scikit-learn |
| Deploy | Docker, Uvicorn, Nginx |

---

## Aviso final

Este projeto é um protótipo de apoio à triagem com IA. Não deve ser usado como diagnóstico clínico. Revisão humana permanece mandatória para todas as saídas.

