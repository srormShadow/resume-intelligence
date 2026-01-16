# Convert any input format into raw text.

# Responsibilities:
# Detect file type safely
# Extract text
# Fail gracefully

# Handles:
# PDF
# DOCX
# Plain text

# Guarantees:
# Never crashes the system
# Returns text or a meaningful error
# No downstream assumptions

# This is document ingestion layer

import os
from typing import Callable

import pdfplumber
from docx import Document as DocxDocument

from core.exception import (
    UnsupportedFileTypeError,
    DocumentParseError
)


def _parse_pdf(path: str) -> str:
    text = []

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception as e:
        raise DocumentParseError(f"Failed to parse PDF: {e}")

    return "\n".join(text).strip()


def _parse_docx(path: str) -> str:
    try:
        doc = DocxDocument(path)
        text = [para.text for para in doc.paragraphs if para.text]
    except Exception as e:
        raise DocumentParseError(f"Failed to parse DOCX: {e}")

    return "\n".join(text).strip()


def _parse_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        raise DocumentParseError(f"Failed to parse text file: {e}")


_PARSERS: dict[str, Callable[[str], str]] = {
    ".pdf": _parse_pdf,
    ".docx": _parse_docx,
    ".txt": _parse_text,
}


def parse_document(path: str) -> str:
    if not path or not os.path.exists(path):
        raise DocumentParseError("File does not exist.")

    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext not in _PARSERS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {ext}"
        )

    raw_text = _PARSERS[ext](path)

    if not raw_text or not raw_text.strip():
        raise DocumentParseError(
            "Parsed document is empty or unreadable."
        )

    return raw_text
