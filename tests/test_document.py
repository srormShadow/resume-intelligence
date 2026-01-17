import pytest

from resume_intelligence.core.document import Document
from resume_intelligence.core.normalizer import normalize_document


def test_document_creation_with_raw_text():
    raw_text = "This is a sample resume."

    doc = Document(raw_text=raw_text)

    assert doc.raw_text == raw_text
    assert doc.clean_text is None
    assert doc.sentences == []


def test_document_normalization_sets_clean_text_and_sentences():
    raw_text = "This is sentence one. This is sentence two."

    doc = Document(raw_text=raw_text)
    normalize_document(doc)

    assert doc.clean_text is not None
    assert isinstance(doc.clean_text, str)

    assert isinstance(doc.sentences, list)
    assert len(doc.sentences) == 2

    assert doc.sentences[0].startswith("this")
    assert doc.sentences[1].startswith("this")


def test_document_normalization_is_idempotent():
    raw_text = "First sentence. Second sentence."

    doc = Document(raw_text=raw_text)
    normalize_document(doc)
    first_sentences = list(doc.sentences)

    normalize_document(doc)
    second_sentences = list(doc.sentences)

    assert first_sentences == second_sentences


def test_document_rejects_empty_raw_text():
    doc = Document(raw_text="")

    with pytest.raises(ValueError):
        normalize_document(doc)


def test_document_sentence_content_is_cleaned():
    raw_text = "  HELLO World!  \nThis IS Test. "

    doc = Document(raw_text=raw_text)
    normalize_document(doc)

    assert doc.sentences == [
        "hello world!",
        "this is test.",
    ]
