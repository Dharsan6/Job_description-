"""Data loading utilities for resumes."""

from __future__ import annotations

import csv
from pathlib import Path

from core.config import DEFAULT_RESUME_CSV, RESUME_COLUMN


def load_resumes(csv_path: Path | str = DEFAULT_RESUME_CSV) -> list[str]:
    """Load resumes from CSV column and clean missing values."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume CSV not found: {path}")

    resumes: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames or RESUME_COLUMN not in reader.fieldnames:
            raise ValueError(f"CSV must contain '{RESUME_COLUMN}' column.")
        for row in reader:
            value = str(row.get(RESUME_COLUMN) or "").strip()
            if value:
                resumes.append(value)

    if not resumes:
        raise ValueError("No valid resumes found in the CSV.")
    return resumes
