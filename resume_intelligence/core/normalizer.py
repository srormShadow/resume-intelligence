# Convert messy human text into standardized machine-friendly text.

# Responsibilities
# Lowercasing (controlled)
# Unicode normalization
# Noise removal
# Whitespace normalization
# Bullet / list preservation
# Sentence boundary detection

import re
import unicodedata
from typing import List

from resume_intelligence.core.document import Document
from resume_intelligence.core.exception import DocumentParseError


BULLET_PATTERNS = [
    r"•",
    r"\u2022",
    r"-",
    r"\*",
]


def _normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _normalize_bullets(text: str) -> str:
    for bullet in BULLET_PATTERNS:
        text = re.sub(rf"\s*{bullet}\s*", ". ", text)
    return text


def _normalize_whitespace(text: str) -> str:
    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize line breaks
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


def _remove_noise_lines(text: str) -> str:
    lines = []

    for line in text.splitlines():
        line = line.strip()

        # Skip decorative separators
        if re.fullmatch(r"[_=\-]{3,}", line):
            continue

        if line:
            lines.append(line)

    return "\n".join(lines)


def _split_sentences(text: str) -> List[str]:
    # Basic sentence split, robust for resumes
    sentences = re.split(r"[.!?]\s+", text)

    return [s.strip() for s in sentences if s.strip()]


def normalize_document(doc: Document) -> Document:
    if not doc or not doc.raw_text:
        raise DocumentParseError("Cannot normalize empty document.")

    text = doc.raw_text

    # 1️⃣ Unicode normalization
    text = _normalize_unicode(text)

    # 2️⃣ Lowercase
    text = text.lower()

    # 3️⃣ Bullet normalization
    text = _normalize_bullets(text)

    # 4️⃣ Remove noisy lines
    text = _remove_noise_lines(text)

    # 5️⃣ Whitespace normalization
    text = _normalize_whitespace(text)

    if not text.strip():
        raise DocumentParseError("Document became empty after normalization.")

    # 6️⃣ Sentence splitting
    sentences = _split_sentences(text)

    doc.set_clean_text(text)
    doc.set_sentences(sentences)

    return doc
