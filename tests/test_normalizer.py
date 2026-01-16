import pytest

from resume_intelligence.core.document import Document
from resume_intelligence.core.normalizer import normalize_document
from resume_intelligence.core.exception import DocumentParseError


def test_normalization_sets_clean_text():
    raw_text = "Flutter Developer with experience in APIs."
    doc = Document(raw_text)

    normalized_doc = normalize_document(doc)

    assert normalized_doc.clean_text is not None
    assert isinstance(normalized_doc.clean_text, str)
    assert len(normalized_doc.clean_text) > 0


def test_normalization_sets_sentences():
    raw_text = "Built APIs. Improved performance."
    doc = Document(raw_text)

    normalized_doc = normalize_document(doc)

    assert normalized_doc.sentences
    assert isinstance(normalized_doc.sentences, list)
    assert len(normalized_doc.sentences) == 2


def test_bullet_normalization():
    raw_text = """
    • Built scalable APIs
    • Improved performance by 30%
    """
    doc = Document(raw_text)

    normalized_doc = normalize_document(doc)
    clean_text = normalized_doc.clean_text
    
    assert clean_text is not None

    assert "built scalable apis" in clean_text
    assert "improved performance by 30%" in clean_text
    assert len(normalized_doc.sentences) == 2


def test_noise_lines_are_removed():
    raw_text = """
    ====================
    Flutter Developer
    --------------------
    Experience in mobile apps
    ====================
    """
    doc = Document(raw_text)

    normalized_doc = normalize_document(doc)
    clean_text = normalized_doc.clean_text
    
    assert clean_text is not None

    assert "flutter developer" in clean_text
    assert "experience in mobile apps" in clean_text
    assert "=" not in clean_text
    assert "-" not in clean_text


def test_unicode_normalization():
    raw_text = "Clean–Architecture and smart quotes “test”"
    doc = Document(raw_text)

    normalized_doc = normalize_document(doc)
    clean_text = normalized_doc.clean_text
    
    assert clean_text is not None

    assert "clean-architecture" in clean_text
    assert "smart quotes" in clean_text


def test_empty_raw_text_raises_error():
    with pytest.raises(ValueError):
        Document("   ")


def test_document_becomes_empty_after_normalization_raises_error():
    raw_text = "-----\n=====\n*****"
    doc = Document(raw_text)

    with pytest.raises(DocumentParseError):
        normalize_document(doc)
