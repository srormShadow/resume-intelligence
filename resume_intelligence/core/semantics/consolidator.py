from typing import Dict, List

from resume_intelligence.core.semantics.concept import Concept


# -------------------------------------------------------------------
# Canonical Concept Map (language-level, NOT domain-specific)
# -------------------------------------------------------------------
_CANONICAL_MAP: Dict[str, str] = {
    # Programming languages
    "use language": "programming languages",
    "modern programming language": "programming languages",

    # Testing
    "unit test": "testing",
    "unit testing": "testing",
    "integration testing": "testing",

    # APIs
    "restful apis": "api integration",

    # Collaboration / planning
    "use collaborate": "collaboration",
    "include plan": "planning",

    # CI/CD
    "ci cd pipeline exposure": "ci cd pipeline",
}


# Concepts that should never survive consolidation
_DROP_ALWAYS = {
    "quality software application",
    "software feature",
    "traffic system",
}


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------
def consolidate_concepts(concepts: List[Concept]) -> List[Concept]:
    merged: Dict[str, Concept] = {}

    for concept in concepts:
        text = concept.text

        if text in _DROP_ALWAYS:
            continue

        canonical = _CANONICAL_MAP.get(text, text)

        if canonical not in merged:
            merged[canonical] = Concept(
                text=canonical,
                confidence=concept.confidence,
                sentences=list(concept.sentences),
                source=concept.source,
                type=concept.type,
            )
        else:
            existing = merged[canonical]

            merged[canonical] = Concept(
                text=canonical,
                confidence=max(existing.confidence, concept.confidence),
                sentences=list(
                    set(existing.sentences + concept.sentences)
                ),
                source=existing.source,
                type=existing.type,
            )

    return list(merged.values())