# Document
#  ├── raw_text
#  ├── cleaned_text
#  ├── sentences
#  ├── paragraphs
#  ├── metadata

from typing import List, Dict, Optional


class Document:
    """
    Canonical representation of a Resume or Job Description.

    This object holds the text at different stages of processing
    and acts as the single source of truth throughout the pipeline.
    """

    def __init__(
        self,
        raw_text: str,
        metadata: Optional[Dict] = None
    ):
        if not isinstance(raw_text, str):
            raise TypeError("raw_text must be a string")

        self.raw_text: str = raw_text
        self.metadata: Optional[Dict] = metadata

        # Populated by normalization
        self.clean_text: Optional[str] = None
        self.sentences: List[str] = []

    def set_clean_text(self, clean_text: str) -> None:
        if not clean_text or not clean_text.strip():
            raise ValueError("Clean text cannot be empty.")

        self.clean_text = clean_text

    def set_sentences(self, sentences: List[str]) -> None:
        if not sentences:
            raise ValueError("Sentences list cannot be empty.")

        self.sentences = sentences

    def is_normalized(self) -> bool:
        return self.clean_text is not None

    def has_sentences(self) -> bool:
        return len(self.sentences) > 0

    def __repr__(self) -> str:
        return (
            f"Document("
            f"raw_text_len={len(self.raw_text)}, "
            f"clean_text_set={self.clean_text is not None}, "
            f"sentences={len(self.sentences)})"
        )
