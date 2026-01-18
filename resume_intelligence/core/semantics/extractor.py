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

import spacy

from resume_intelligence.core.document import Document
from resume_intelligence.core.semantics.concept import Concept, ConceptSource, ConceptType


# -------------------------------------------------------------------
# spaCy model (loaded once for performance)
# -------------------------------------------------------------------
_NLP = None

def get_nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


# -------------------------------------------------------------------
# Linguistic cleanup / normalization
# -------------------------------------------------------------------
_STOP_FILLERS = {
    "with", "using", "and", "or", "of", "in", "on", "for", "to"
}

_GENERIC_CONCEPTS = {
    "role",
    "responsibility",
    "experience",
    "task",
    "technique",
    "ability",
    "knowledge",
    "understanding",
    "familiarity",
}

_EMPHASIS_WORDS = {
    "experience",
    "experienced",
    "expertise",
    "strong",
    "required",
    "responsible",
    "responsibility",
}

_GENERIC_CONFIDENCE_CAP = 0.4


# -------------------------------------------------------------------
# Verb canonicalization (semantic normalization)
# -------------------------------------------------------------------
_VERB_CANONICAL_MAP = {
    "implement": "development",
    "build": "development",
    "develop": "development",
    "deliver": "delivery",
    "write": "testing",
    "test": "testing",
    "debug": "debugging",
    "resolve": "debugging",
    "fix": "debugging",
    "optimize": "performance optimization",
    "ensure": "performance optimization",
    "improve": "performance optimization",
    "integrate": "integration",
    "design": "design",
    "collaborate": "collaboration",
}

_ROLE_KEYWORDS = {
    "engineer", "manager", "candidate", "team", "role"
}

_PRACTICE_KEYWORDS = {
    "testing", "review", "planning", "optimization", "debugging"
}

_TOOL_KEYWORDS = {
    "platform", "system", "pipeline", "framework", "tool"
}


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _normalize_phrase(text: str) -> str:
    """Normalize a phrase into canonical form."""
    nlp = get_nlp()
    doc = nlp(text.lower().strip())
    tokens = [
        token.lemma_
        for token in doc
        if token.is_alpha and token.lemma_ not in _STOP_FILLERS
    ]
    return " ".join(tokens)


def _is_valid_concept(text: str) -> bool:
    """Decide whether a phrase represents a valid semantic concept."""
    tokens = text.split()

    # Rule 1: minimum semantic length
    if len(tokens) < 2:
        return False

    # Rule 2: reject generic/meta concepts
    if any(token in _GENERIC_CONCEPTS for token in tokens):
        return False

    # Rule 3: alphabetic only
    if not all(token.isalpha() for token in tokens):
        return False

    return True


def _extract_noun_phrases(doc) -> List[str]:
    """Extract noun phrases (skills, tools, domains)."""
    phrases: List[str] = []

    for chunk in doc.noun_chunks:
        words = [t.text for t in chunk if t.is_alpha]
        if 1 <= len(words) <= 4:
            phrases.append(" ".join(words))

    return phrases


def _extract_verb_object_concepts(doc) -> List[str]:
    """Extract and canonicalize verb-based experience concepts."""
    concepts: List[str] = []

    for token in doc:
        if token.pos_ == "VERB":
            verb = token.lemma_

            # Canonicalize verb if possible
            if verb in _VERB_CANONICAL_MAP:
                concepts.append(_VERB_CANONICAL_MAP[verb])
            else:
                for child in token.children:
                    if child.dep_ in {"dobj", "pobj"} and child.is_alpha:
                        concepts.append(f"{verb} {child.lemma_}")

    return concepts


def _calculate_confidence(
    phrase: str,
    sentences: List[str],
    came_from_action: bool,
) -> float:
    """Compute confidence score for a concept."""

    # 1️⃣ Frequency (max contribution = 0.5)
    freq_score = min(len(sentences) / 3.0, 1.0) * 0.5

    # 2️⃣ Linguistic strength
    linguistic_bonus = 0.3 if came_from_action else 0.15

    # 3️⃣ Emphasis bonus
    emphasis_bonus = 0.0
    for s in sentences:
        if any(word in s.lower() for word in _EMPHASIS_WORDS):
            emphasis_bonus = 0.2
            break

    confidence = freq_score + linguistic_bonus + emphasis_bonus

    # 4️⃣ Cap overly generic concepts
    if phrase in {"software engineer", "software development"}:
        confidence = min(confidence, _GENERIC_CONFIDENCE_CAP)

    return round(min(confidence, 1.0), 2)


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------
def extract_concepts(
    document: Document,
    source: ConceptSource,
) -> List[Concept]:
    """
    Extract semantic concepts from a normalized Document.
    """

    if not document.sentences:
        raise ValueError("Document must be normalized before concept extraction.")

    phrase_to_data: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "sentences": [],
            "from_action": False,
        }
    )

    # ---- Sentence-level processing
    for sentence in document.sentences:
        nlp = get_nlp()
        spacy_doc = nlp(sentence)

        # Noun phrases
        for phrase in _extract_noun_phrases(spacy_doc):
            normalized = _normalize_phrase(phrase)
            if normalized:
                phrase_to_data[normalized]["sentences"].append(sentence)

        # Verb-based concepts (canonicalized)
        for phrase in _extract_verb_object_concepts(spacy_doc):
            normalized = _normalize_phrase(phrase)
            if normalized:
                phrase_to_data[normalized]["sentences"].append(sentence)
                phrase_to_data[normalized]["from_action"] = True

    # ---- Build Concept objects
    concepts: List[Concept] = []

    for phrase, data in phrase_to_data.items():
        if not _is_valid_concept(phrase):
            continue

        confidence = _calculate_confidence(
            phrase=phrase,
            sentences=data["sentences"],
            came_from_action=data["from_action"],
        )

        concept_type = _infer_concept_type(phrase)

        if concept_type == "role_context":
            continue

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

def _infer_concept_type(text: str) -> ConceptType:
    tokens = set(text.split())

    if tokens & _ROLE_KEYWORDS:
        return ConceptType.ROLE_CONTEXT

    if tokens & _PRACTICE_KEYWORDS:
        return ConceptType.PRACTICE

    if tokens & _TOOL_KEYWORDS:
        return ConceptType.TOOL

    return ConceptType.SKILL
