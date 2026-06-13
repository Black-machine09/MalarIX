# Malaria Triage AI — Prompt para Frontend

## 1) Visão geral
Frontend que consome a API FastAPI do projeto **Malaria Triage AI** (MalarIX).

- Backend roda em: `http://localhost:8000`
- A API é **sem autenticação**.
- A inferência é feita via endpoint **multipart/form-data** com campo **`files`**.

> Todos os textos devem ser em **pt-BR**.

---

## 2) Endpoints da API (para o frontend consumir)

### `GET /health`
- URL: `http://localhost:8000/health`
- Método: `GET`

**200**
```json
{ "status": "ok" }
```

---

### `POST /api/v1/exams`
Cria um paciente e um exame no SQLite e retorna um `exam_id`.

- URL: `http://localhost:8000/api/v1/exams`
- Método: `POST`
- Content-Type: `application/json`

**Body**
```json
{
  "patient_name": "Maria Silva",
  "birth_date": "1990-01-01",
  "gender": "F",
  "exam_date": "2026-06-12"
}
```

**200**
```json
{ "status": "ok", "exam_id": "<string>" }
```

---

### `POST /api/v1/predict-batch`
Envia de 1 a N imagens para triagem em lote.

- URL: `http://localhost:8000/api/v1/predict-batch?exam_id=<EXAM_ID>`
- Método: `POST`
- Content-Type: `multipart/form-data`

**Regras**
- Query param obrigatório: `exam_id`
- Body form-data obrigatório:
  - `files`: **file[]** (adicione uma linha por arquivo; o nome do campo tem que ser exatamente `files`)

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

**Labels retornados**
- `suspected_positive`
- `likely_negative`

**Erros (corpo padrão)**
```json
{ "error": "<code>", "message": "<human message>" }
```

**Códigos frequentes**
- `400 no_images_provided`
- `400 exam_id_required`
- `400 too_many_images`
- `413 file_too_large`
- `415 unsupported_media_type`
- `422 image_decode_failed`
- `422 image_quality_insufficient`
- `500 model_not_loaded`

---

### `GET /api/v1/occurrences`
Lista triagens armazenadas.

- URL: `http://localhost:8000/api/v1/occurrences`
- Método: `GET`

**Query params**
- `limit` (default 20)
- `offset` (default 0)

**200 (estrutura)**
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
Resumo por dia.

- URL: `http://localhost:8000/api/v1/stats/dashboard`
- Método: `GET`

**200 (estrutura)**
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

## 3) Fluxos de UI obrigatórios

### Página 1 — Dashboard / Início `/`
- Botão: **“Nova Triagem”**
- Cards com:
  - total de triagens
  - suspeitos positivos
  - provavelmente negativos
  - (se disponível) incertos
- Lista curta das últimas ocorrências (pode vir do `/occurrences`).

### Página 2 — Nova Triagem `/triage`
**Form + Upload**
1. Campos para cadastrar:
   - `patient_name`
   - `birth_date`
   - `gender`
   - `exam_date`
2. Upload de imagens (multi-select / drag & drop):
   - aceitar apenas `.jpg/.jpeg/.png`
3. Ao clicar em **“Analisar”**:
   - Chamar `POST /api/v1/exams` para obter `exam_id`
   - Montar `FormData` com `files[]` (nome do campo = `files`)
   - Chamar `POST /api/v1/predict-batch?exam_id=...`

**Estados**
- Loading: spinner/progresso durante upload e inferência
- Erro: exibir `error` e `message` retornados pela API
- Sucesso:
  - Exibir badge/cor por label:
    - `suspected_positive` → **vermelho**
    - `likely_negative` → **verde**
  - Mostrar `confidence`, `images_processed`, `images_rejected` e `model_version`

### Página 3 — Histórico `/history`
- Tabela/painel com ocorrências
- Paginação via `limit/offset`
- Filtros opcionais por label e período

---

## 4) Requisitos de integração
- Tratar CORS (backend já libera `*`).
- Recomendado: usar um “API client” centralizado para:
  - `health`, `create exam`, `predict`, `occurrences`, `stats`
- Montar `FormData` corretamente:
  - cada arquivo precisa ser anexado com a mesma key: `files`

---

## 5) Stack recomendada (escolha uma)
- React + Vite + TypeScript + Tailwind
- ou Next.js + Tailwind

---

## 6) Entregáveis
1. Frontend completo com 3 páginas (dashboard/triage/history)
2. Integração com **todos** os endpoints listados acima
3. Tratamento de loading/erro/vazio
4. UI responsiva e consistente

