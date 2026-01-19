# In phrase extraction

# 🔹 A. Noun Phrases (Primary Signal)

# Most skills and tools are noun phrases.
# Examples:
# “clean architecture”
# “state management”
# “unit testing”
# “api integration”

# Extraction rule:
# Extract noun chunks with 1–4 words
# Why limit length?
# Too short → noise
# Too long → entire sentences

# 🔹 B. Verb–Object Pairs (Experience Signal)

# Experience is often expressed as:
# VERB + OBJECT
# Examples:
# “built APIs”
# “optimized performance”
# “designed architecture”
# “implemented authentication”

# This is how you extract experience, not just skills.

# 🔹 C. Action–Impact Statements (Bonus Signal)

# Sentences like:
# Improved performance by 30%
# Reduced latency
# Increased reliability

# These indicate seniority and impact.
# We extract:
# The action concept (performance optimization)
# Store the sentence for explanation

from collections import defaultdict
from typing import Any, Dict, List

from resume_intelligence.core.document import Document
from resume_intelligence.core.semantics.concept import (
    Concept,
    ConceptSource,
    ConceptType,
)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

_STOP_WORDS = {
    "with", "using", "and", "or", "of", "in", "on", "for", "to",
    "a", "an", "the", "this", "that", "is", "are", "was", "were",
}

_GENERIC_CONCEPTS = {
    "role", "responsibility", "experience", "task",
    "technique", "ability", "knowledge", "understanding",
}

_EMPHASIS_WORDS = {
    "experience", "experienced", "expertise", "strong",
    "required", "responsible", "responsibility",
}

_GENERIC_CONFIDENCE_CAP = 0.4

# -------------------------------------------------------------------
# Verb semantics (ATS-friendly)
# -------------------------------------------------------------------

_ACTION_VERBS = {
    "build", "develop", "implement", "design", "integrate",
    "optimize", "test", "debug", "deploy", "maintain",
    "review", "plan", "collaborate", "deliver",
}

_VERB_CANONICAL_MAP = {
    "build": "development",
    "develop": "development",
    "implement": "development",
    "optimize": "performance optimization",
    "improve": "performance optimization",
    "test": "testing",
    "debug": "debugging",
    "deploy": "deployment",
    "integrate": "api integration",
    "review": "code review",
    "plan": "planning",
    "collaborate": "collaboration",
}

# -------------------------------------------------------------------
# Concept typing keywords
# -------------------------------------------------------------------

_ROLE_KEYWORDS = {"engineer", "developer", "manager", "team", "role"}
_PRACTICE_KEYWORDS = {"testing", "review", "planning", "debugging", "optimization"}
_TOOL_KEYWORDS = {"tool", "platform", "framework", "pipeline", "system"}

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    return [
        t for t in text.lower().split()
        if t.isalpha() and t not in _STOP_WORDS
    ]


def _extract_ngrams(tokens: List[str], min_n=2, max_n=4) -> List[str]:
    phrases = []
    for n in range(min_n, max_n + 1):
        for i in range(len(tokens) - n + 1):
            phrases.append(" ".join(tokens[i:i + n]))
    return phrases


def _is_valid_concept(text: str) -> bool:
    tokens = text.split()

    if len(tokens) < 2:
        return False

    if any(t in _GENERIC_CONCEPTS for t in tokens):
        return False

    return True


def _calculate_confidence(
    phrase: str,
    sentences: List[str],
    from_action: bool,
) -> float:
    freq_score = min(len(sentences) / 3.0, 1.0) * 0.5
    action_bonus = 0.3 if from_action else 0.15

    emphasis_bonus = 0.0
    for s in sentences:
        if any(w in s.lower() for w in _EMPHASIS_WORDS):
            emphasis_bonus = 0.2
            break

    confidence = freq_score + action_bonus + emphasis_bonus

    if phrase in {"software engineer", "software development"}:
        confidence = min(confidence, _GENERIC_CONFIDENCE_CAP)

    return round(min(confidence, 1.0), 2)


def _infer_concept_type(text: str) -> ConceptType:
    tokens = set(text.split())

    if tokens & _ROLE_KEYWORDS:
        return ConceptType.ROLE_CONTEXT
    if tokens & _PRACTICE_KEYWORDS:
        return ConceptType.PRACTICE
    if tokens & _TOOL_KEYWORDS:
        return ConceptType.TOOL

    return ConceptType.SKILL


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def extract_concepts(
    document: Document,
    source: ConceptSource,
) -> List[Concept]:

    if not document.sentences:
        raise ValueError("Document must be normalized before concept extraction.")

    phrase_to_data: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"sentences": [], "from_action": False}
    )

    for sentence in document.sentences:
        tokens = _tokenize(sentence)

        # 1️⃣ N-gram noun-like concepts
        for phrase in _extract_ngrams(tokens):
            phrase_to_data[phrase]["sentences"].append(sentence)

        # 2️⃣ Verb-driven concepts
        for token in tokens:
            if token in _ACTION_VERBS:
                canonical = _VERB_CANONICAL_MAP.get(token)
                if canonical:
                    phrase_to_data[canonical]["sentences"].append(sentence)
                    phrase_to_data[canonical]["from_action"] = True

    concepts: List[Concept] = []

    for phrase, data in phrase_to_data.items():
        if not _is_valid_concept(phrase):
            continue

        concept_type = _infer_concept_type(phrase)
        if concept_type == ConceptType.ROLE_CONTEXT:
            continue

        confidence = _calculate_confidence(
            phrase=phrase,
            sentences=data["sentences"],
            from_action=data["from_action"],
        )

        concepts.append(
            Concept(
                text=phrase,
                confidence=confidence,
                sentences=list(set(data["sentences"])),
                source=source,
                type=concept_type,
            )
        )

    return concepts
