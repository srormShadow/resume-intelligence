# Concept
#  ├── text
#  ├── type (skill / tool / practice / domain)
#  ├── confidence
#  ├── source_sentences

# Purpose
# Extract meaningful concepts from normalized text.

# This is where we use:
# Linguistic structure
# Noun phrases
# Dependency patterns
# Controlled heuristics

# Responsibilities:
# Extract multi-word phrases
# Deduplicate semantically similar phrases
# Preserve sentence context

# A concept is:
# A meaningful idea expressed in text that represents a skill, tool, practice, responsibility, or domain knowledge — independent of 
# exact wording.

from dataclasses import dataclass
from typing import List, Literal

ConceptType = Literal[
    "skill",
    "practice",
    "tool",
    "role_context",
]

ConceptSource = Literal["resume", "jd"]


@dataclass(frozen=True)
class Concept:
    """
    Represents a meaningful semantic concept extracted from a document.
    """

    text: str
    confidence: float
    sentences: List[str]
    source: ConceptSource
    type: ConceptType

#     Concept(
#       text="state management",
#       confidence=0.82,
#       sentences=["used mobx for state management in flutter apps"],
#       source="resume"
#     )


    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Concept text cannot be empty.")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Concept confidence must be between 0.0 and 1.0.")

        if not self.sentences:
            raise ValueError("Concept must reference at least one sentence.")
