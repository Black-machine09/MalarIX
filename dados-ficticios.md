# Dados Fictícios — MalariaDetect

Este documento descreve todos os dados fictícios utilizados nas telas do sistema, servindo como referência para a construção do backend.

---

## 1. TopBar (presente em todas as telas)

| Campo | Valor |
|---|---|
| Sistema | MalariaDetect — Sistema de Diagnóstico |
| Usuário logado | Dr. Ana Costa |
| Especialidade | Hematologista |
| Nav | Nova Análise, Histórico, Estatísticas |

---

## 2. Tela de Upload / Triagem (`triage.html`)

### 2.1 Metadados da Imagem

| Campo | Valor |
|---|---|
| Nome do arquivo | `sample_001.tiff` |
| Tamanho | 4.2 MB |
| Dimensões | 2048 × 1536 px |
| Coloração | Giemsa |
| Ampliação | 100× |
| Preview | `sample_blood_smear_001.tiff` |

### 2.2 Dados do Paciente

| Campo | Placeholder |
|---|---|
| Nome Completo | Ex: João Silva |
| Data de Nascimento | DD/MM/AAAA |
| Gênero | Selecionar (dropdown) |
| Nº Prontuário | Ex: PAC-000123 |

### 2.3 Configurações de Upload

- Formatos aceitos: **PNG, JPG, TIFF**
- Tamanho máximo: **20 MB**

---

## 3. Tela de Resultado (`result.html`)

### 3.1 Diagnóstico

| Campo | Valor |
|---|---|
| Resultado | **Positivo** |
| Subtítulo | Malária detectada |
| Status espécime | Plasmodium: Presente |
| Confiança da IA | **97.4%** |
| Espécie identificada | **Plasmodium falciparum** |
| Estágio | Trofozoíto |
| Parasitemia | 3.2% |
| Células infectadas | ~32/µL |

### 3.2 Dados do Paciente (resultado)

| Campo | Valor |
|---|---|
| Nome | João Mendes Silva |
| Data de Nascimento | 14/03/1988 |
| Gênero | Masculino |
| Nº Prontuário | PAC-000847 |
| Data do Exame | 23/07/2025 — 14:32 |
| Médico responsável | Dr. Ana Costa |

### 3.3 Parâmetros Hematológicos

| Parâmetro | Valor | Ref. | Status |
|---|---|---|---|
| Hemoglobina | 9.2 g/dL | 12.0 – 16.0 | 🔴 Baixo |
| Hematócrito | 28% | 36 – 48 | 🔴 Baixo |
| Eritrócitos | 3.1 M/µL | 3.8 – 5.2 | 🔴 Baixo |
| Leucócitos | 11.4 K/µL | 4.5 – 11.0 | 🟡 Alto |
| Plaquetas | 82 K/µL | 150 – 400 | 🔴 Baixo |
| VCM | 74 fL | 80 – 100 | 🔴 Baixo |
| HCM | 22.1 pg | 27 – 33 | 🔴 Baixo |
| Neutrófilos | 78% | 50 – 70 | 🟡 Alto |
| Linfócitos | 14% | 20 – 40 | 🔴 Baixo |

**Regras de status:**
- 🔴 **Baixo** (`bg-danger-bg text-danger`): valor abaixo do ref. inferior
- 🟡 **Alto** (`bg-warning-bg text-warning`): valor acima do ref. superior
- 🟢 Normal: dentro do intervalo de referência

### 3.4 Observações Clínicas

| Nível | Observação |
|---|---|
| 🔴 Grave | Anemia hemolítica severa: hemoglobina e hematócrito criticamente baixos — compatíveis com destruição eritrocitária por Plasmodium falciparum. |
| 🔴 Grave | Trombocitopenia significativa (82 K/µL): risco aumentado de sangramento — monitoramento intensivo recomendado. |
| 🟡 Atenção | Leucocitose com neutrofilia relativa: resposta inflamatória ativa. Descartar infecção bacteriana secundária. |
| 🟢 Info | Morfologia eritrocitária compatível com microcitose e hipocromia — possivelmente anemia ferropriva subjacente. |

### 3.5 Conduta Recomendada

| Medicamento / Ação | Detalhes |
|---|---|
| 💊 Artemeter + Lumefantrina | Protocolo de 1ª linha para P. falciparum |
| 🌡️ Monitorar sinais vitais | A cada 4h nas primeiras 24 horas |
| 💧 Hidratação venosa | Soro fisiológico 0.9% — 1000mL/6h |
| 📅 Retorno em 48h | Hemograma de controle e parasitemia |

### 3.6 Imagem Analisada

A imagem do resultado contém marcações visuais da IA:
- 🔴 Círculos vermelhos indicam células **infectadas**
- 🟢 Células **saudáveis** (sem marcação)

---

## 4. Tela de Login / Registro (`auth.html`)

### 4.1 Login

| Campo | Placeholder / Tipo |
|---|---|
| E-mail | `seu@email.com` (texto) |
| Senha | `••••••••` (password) |
| Manter conectado | checkbox |
| Esqueceu a senha? | link |
| Botão | **Entrar** |

### 4.2 Registro

| Campo | Placeholder / Tipo |
|---|---|
| Nome Completo | Ex: Maria Oliveira |
| E-mail | `seu@email.com` |
| Senha | `••••••••` |
| Confirmar Senha | `••••••••` |
| Aceitar Termos | checkbox — Termos de Uso e Política de Privacidade |
| Botão | **Criar Conta** |

---

## 5. Estrutura de Dados Sugerida para API

### `POST /auth/login`

```json
{
  "email": "ana.costa@hospital.com",
  "password": "********",
  "remember": true
}
```

**Resposta:**
```json
{
  "token": "jwt-token-aqui",
  "user": {
    "name": "Dr. Ana Costa",
    "specialty": "Hematologista",
    "avatar": null
  }
}
```

### `POST /auth/register`

```json
{
  "name": "Maria Oliveira",
  "email": "maria@hospital.com",
  "password": "********",
  "confirmPassword": "********",
  "acceptTerms": true
}
```

### `POST /api/analyze`

```json
{
  "image": "(base64 ou file multipart)",
  "patient": {
    "name": "João Mendes Silva",
    "birthDate": "1988-03-14",
    "gender": "M",
    "medicalRecord": "PAC-000847"
  }
}
```

### `GET /api/result/{id}` — Resposta

```json
{
  "id": "res-001",
  "status": "completed",
  "diagnosis": {
    "result": "positive",
    "label": "Positivo",
    "subtitle": "Malária detectada",
    "species": "Plasmodium falciparum",
    "speciesStatus": "Presente",
    "stage": "Trofozoíto",
    "confidence": 97.4,
    "parasitemia": 3.2,
    "infectedCells": 32,
    "infectedCellsUnit": "/µL"
  },
  "patient": {
    "name": "João Mendes Silva",
    "birthDate": "1988-03-14",
    "gender": "Masculino",
    "medicalRecord": "PAC-000847",
    "examDate": "2025-07-23T14:32:00",
    "physician": "Dr. Ana Costa"
  },
  "hematology": {
    "hemoglobin": { "value": 9.2, "unit": "g/dL", "refMin": 12.0, "refMax": 16.0, "status": "low" },
    "hematocrit": { "value": 28, "unit": "%", "refMin": 36, "refMax": 48, "status": "low" },
    "erythrocytes": { "value": 3.1, "unit": "M/µL", "refMin": 3.8, "refMax": 5.2, "status": "low" },
    "leukocytes": { "value": 11.4, "unit": "K/µL", "refMin": 4.5, "refMax": 11.0, "status": "high" },
    "platelets": { "value": 82, "unit": "K/µL", "refMin": 150, "refMax": 400, "status": "low" },
    "mcv": { "value": 74, "unit": "fL", "refMin": 80, "refMax": 100, "status": "low" },
    "mch": { "value": 22.1, "unit": "pg", "refMin": 27, "refMax": 33, "status": "low" },
    "neutrophils": { "value": 78, "unit": "%", "refMin": 50, "refMax": 70, "status": "high" },
    "lymphocytes": { "value": 14, "unit": "%", "refMin": 20, "refMax": 40, "status": "low" }
  },
  "observations": [
    {
      "severity": "critical",
      "text": "Anemia hemolítica severa: hemoglobina e hematócrito criticamente baixos — compatíveis com destruição eritrocitária por Plasmodium falciparum."
    },
    {
      "severity": "critical",
      "text": "Trombocitopenia significativa (82 K/µL): risco aumentado de sangramento — monitoramento intensivo recomendado."
    },
    {
      "severity": "warning",
      "text": "Leucocitose com neutrofilia relativa: resposta inflamatória ativa. Descartar infecção bacteriana secundária."
    },
    {
      "severity": "info",
      "text": "Morfologia eritrocitária compatível com microcitose e hipocromia — possivelmente anemia ferropriva subjacente."
    }
  ],
  "recommendations": [
    {
      "icon": "pill",
      "title": "Artemeter + Lumefantrina",
      "description": "Protocolo de 1ª linha para P. falciparum"
    },
    {
      "icon": "thermometer",
      "title": "Monitorar sinais vitais",
      "description": "A cada 4h nas primeiras 24 horas"
    },
    {
      "icon": "droplets",
      "title": "Hidratação venosa",
      "description": "Soro fisiológico 0.9% — 1000mL/6h"
    },
    {
      "icon": "calendar-check",
      "title": "Retorno em 48h",
      "description": "Hemograma de controle e parasitemia"
    }
  ],
  "imageUrl": "https://storage.googleapis.com/banani-generated-images/generated-images/02df3e24-91db-444c-b6e4-c02e793cd352.jpg"
}
```

### `GET /api/uploads` — Histórico (esboço)

```json
[
  {
    "id": "res-001",
    "patientName": "João Mendes Silva",
    "examDate": "2025-07-23T14:32:00",
    "result": "positive",
    "confidence": 97.4,
    "species": "Plasmodium falciparum"
  }
]
```

---

## 6. Observações sobre o Tema (Tokens CSS)

Todas as telas usam Tailwind CSS v4.3 com os seguintes tokens:

```css
--color-background: #f0f4f8;
--color-foreground: #0d1b2a;
--color-border: #d1dde8;
--color-input: #ffffff;
--color-primary: #1a6fc4;
--color-primary-foreground: #ffffff;
--color-secondary: #e3edf7;
--color-muted: #e8eef4;
--color-muted-foreground: #6b7f93;
--color-surface: #ffffff;
--color-success: #1aab6d;
--color-danger: #e53e3e;
--color-warning: #d97706;
--font-body: Inter;
--font-headings: Inter;
```

Status hematológicos seguem o padrão:
- **low** → `bg-danger-bg` / `text-danger`
- **high** → `bg-warning-bg` / `text-warning`
