from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4


def _get_db_path() -> Path:
    # Keep it local to the repo/workspace by default.
    # Can be overridden via env var DB_PATH.
    db_path = os.getenv("DB_PATH")
    if db_path:
        return Path(db_path)
    return Path(os.getenv("SQLITE_PATH", "malaria_triage.sqlite3"))


DB_PATH = _get_db_path()


@contextmanager
def get_conn() -> "Any":
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()



def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                gender TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exams (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS triages (
                id TEXT PRIMARY KEY,
                exam_id TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL NOT NULL,
                images_processed INTEGER NOT NULL,
                images_rejected INTEGER NOT NULL,
                model_version TEXT NOT NULL,
                decode_failures INTEGER NOT NULL,
                quality_failures INTEGER NOT NULL,
                quality_reasons TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(exam_id) REFERENCES exams(id)
            )
            """
        )


def utc_now_iso() -> str:
    # Using stdlib only; avoid pytz dependency.
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_patient(name: str, birth_date: str, gender: str) -> str:
    patient_id = uuid4().hex
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO patients (id, name, birth_date, gender, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (patient_id, name, birth_date, gender, utc_now_iso()),
        )
    return patient_id


def create_exam(patient_id: str, exam_date: str) -> str:
    exam_id = uuid4().hex
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO exams (id, patient_id, exam_date, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (exam_id, patient_id, exam_date, utc_now_iso()),
        )
    return exam_id


def create_triage(
    exam_id: str,
    *,
    label: str,
    confidence: float,
    images_processed: int,
    images_rejected: int,
    model_version: str,
    decode_failures: int,
    quality_failures: int,
    quality_reasons: dict[str, int] | None = None,
) -> str:
    triage_id = uuid4().hex
    import json

    qr = json.dumps(quality_reasons, ensure_ascii=False) if quality_reasons else None

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO triages (
                id, exam_id, label, confidence,
                images_processed, images_rejected,
                model_version,
                decode_failures, quality_failures,
                quality_reasons,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                triage_id,
                exam_id,
                label,
                confidence,
                images_processed,
                images_rejected,
                model_version,
                decode_failures,
                quality_failures,
                qr,
                utc_now_iso(),
            ),
        )

    return triage_id


def get_patient_by_id(patient_id: str) -> "Any":

    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        return cur.fetchone()


def list_triages(limit: int, offset: int) -> tuple[int, list[dict[str, Any]]]:
    limit = max(1, min(100, int(limit)))
    offset = max(0, int(offset))

    with get_conn() as conn:
        total_row = conn.execute("SELECT COUNT(*) as c FROM triages").fetchone()
        total = int(total_row["c"]) if total_row else 0

        rows = conn.execute(
            """
            SELECT
                t.id as triage_id,
                t.created_at as created_at,
                t.label as label,
                t.confidence as confidence,
                t.images_processed as images_processed,
                t.images_rejected as images_rejected,
                t.model_version as model_version,
                e.id as exam_id,
                e.exam_date as exam_date,
                p.name as patient_name,
                p.birth_date as birth_date,
                p.gender as gender
            FROM triages t
            JOIN exams e ON e.id = t.exam_id
            JOIN patients p ON p.id = e.patient_id
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

        items: list[dict[str, Any]] = []
        for r in rows:
            items.append({k: r[k] for k in r.keys()})
        return total, items


def dashboard_by_day() -> dict[str, Any]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                date(t.created_at) as day,
                SUM(CASE WHEN t.label = 'suspected_positive' THEN 1 ELSE 0 END) as suspected_positive,
                SUM(CASE WHEN t.label = 'likely_negative' THEN 1 ELSE 0 END) as likely_negative,
                SUM(CASE WHEN t.label = 'uncertain' THEN 1 ELSE 0 END) as uncertain
            FROM triages t
            GROUP BY date(t.created_at)
            ORDER BY day DESC
            LIMIT 30
            """,
        ).fetchall()

        summary_row = conn.execute(
            """
            SELECT
                COUNT(*) as total_occurrences,
                SUM(CASE WHEN t.label = 'suspected_positive' THEN 1 ELSE 0 END) as suspected_positive,
                SUM(CASE WHEN t.label = 'uncertain' THEN 1 ELSE 0 END) as uncertain,
                SUM(CASE WHEN t.label = 'likely_negative' THEN 1 ELSE 0 END) as likely_negative
            FROM triages t
            """,
        ).fetchone()

        summary = {
            "total_occurrences": int(summary_row["total_occurrences"]) if summary_row else 0,
            "suspected_positive": int(summary_row["suspected_positive"]) if summary_row else 0,
            "uncertain": int(summary_row["uncertain"]) if summary_row else 0,
            "likely_negative": int(summary_row["likely_negative"]) if summary_row else 0,
        }

        time_series = []
        for r in rows:
            time_series.append(
                {
                    "day": r["day"],
                    "suspected_positive": int(r["suspected_positive"]),
                    "uncertain": int(r["uncertain"]),
                    "likely_negative": int(r["likely_negative"]),
                }
            )

    return {"summary": summary, "time_series": list(reversed(time_series))}

