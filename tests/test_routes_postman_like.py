import json
import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _set_test_db(tmp_path) -> Generator[None, None, None]:
    # Isola o SQLite para não sujar o arquivo real do projeto
    db_file = tmp_path / "test-malaria_triage.sqlite3"
    os.environ["SQLITE_PATH"] = str(db_file)
    yield


def _client() -> TestClient:
    # Importar depois de setar SQLITE_PATH garante que a DB use o path de teste
    from app import create_app

    return TestClient(create_app())


def test_create_exam_ok() -> None:
    client = _client()

    payload = {
        "patient_name": "Maria Silva",
        "birth_date": "1990-01-01",
        "gender": "F",
        "exam_date": "2026-06-12",
    }

    resp = client.post("/api/v1/exams", json=payload)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["exam_id"], str)
    assert len(data["exam_id"]) > 0


def test_create_exam_validation_error() -> None:
    client = _client()

    # Falta campos obrigatórios
    payload = {
        "patient_name": "Maria Silva",
    }

    resp = client.post("/api/v1/exams", json=payload)
    assert resp.status_code == 422

