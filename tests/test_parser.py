import tempfile
import os
import pytest

from resume_intelligence.core.parser import parse_document
from resume_intelligence.core.exception import (
    DocumentParseError,
    UnsupportedFileTypeError,
)


def test_parse_text_file_success():
    content = "Flutter Developer with API experience."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parsed_text = parse_document(tmp_path)
        assert content in parsed_text
    finally:
        os.remove(tmp_path)


def test_parse_text_file_empty_raises_error():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write("")
        tmp_path = tmp.name

    try:
        with pytest.raises(DocumentParseError):
            parse_document(tmp_path)
    finally:
        os.remove(tmp_path)


def test_unsupported_file_type():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(b"data,data")
        tmp_path = tmp.name

    try:
        with pytest.raises(UnsupportedFileTypeError):
            parse_document(tmp_path)
    finally:
        os.remove(tmp_path)


def test_missing_file_raises_error():
    with pytest.raises(DocumentParseError):
        parse_document("this_file_does_not_exist.pdf")
