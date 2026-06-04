"""Resume document parsing helpers."""

from __future__ import annotations

import io
from pathlib import Path


def parse_uploaded_resume(filename: str, file_bytes: bytes) -> str:
    """Extract text from PDF, DOC, DOCX, or TXT uploads."""
    extension = Path(filename.lower()).suffix

    if extension == ".pdf":
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if extension in {".txt", ".doc", ".docx"}:
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                return file_bytes.decode(encoding, errors="ignore").strip()
            except Exception:
                continue
        return ""

    raise ValueError("Unsupported file type. Please upload PDF, DOC, DOCX, or TXT.")
