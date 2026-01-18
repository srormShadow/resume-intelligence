# JD concepts:
# api integration        (skill, confidence=0.8)
# cloud platform         (tool, confidence=0.6)
# testing                (practice, confidence=0.7)

# Similarity scores:
# api integration → 0.86
# cloud platform  → 0.20
# testing         → 0.80

# Weighted math:
# api integration: 1.0 × 0.8 × 0.86 = 0.688
# cloud platform:  0.6 × 0.6 × 0.20 = 0.072
# testing:         0.8 × 0.7 × 0.80 = 0.448
# ------------------------------------
# total = 1.208
# possible = 1.0×0.8 + 0.6×0.6 + 0.8×0.7 = 1.72

# ATS score = 1.208 / 1.72 = 70.2%
from typing import Dict, List

from resume_intelligence.core.semantics.concept import Concept, ConceptType


TYPE_WEIGHTS = {
    ConceptType.SKILL: 1.0,
    ConceptType.TOOL: 0.9,
    ConceptType.PRACTICE: 0.8,
    ConceptType.ROLE_CONTEXT: 0.3,
}

MATCH_QUALITY_WEIGHTS = {
    "matched": 1.0,
    "partial": 0.7,
    "missing": 0.0,
}


def compute_ats_score(
    jd_concepts: List[Concept],
    match_results: Dict[str, List[Dict]],
) -> float:
    """
    Compute ATS match score between JD and resume.

    Args:
        jd_concepts: Original JD Concept objects
        match_results: Output of ConceptMatcher.match()

    Returns:
        ATS score as a percentage (0–100)
    """

    # Map JD concept → similarity score
    match_map = {}

    for bucket in ("matched", "partial", "missing"):
        for record in match_results[bucket]:
            match_map[record["jd_concept"]] = {
                "similarity": record["score"],
                "bucket": bucket,
            }

    total_weighted_score = 0.0
    total_possible_score = 0.0

    for concept in jd_concepts:
        confidence = concept.confidence
        type_weight = TYPE_WEIGHTS.get(concept.type, 0.5)

        base_weight = confidence * type_weight
        total_possible_score += base_weight

        entry = match_map.get(concept.text)
        if not entry:
            continue

        similarity = entry["similarity"]
        quality_weight = MATCH_QUALITY_WEIGHTS[entry["bucket"]]

        # similarity floor
        if similarity < 0.4:
            continue

        # similarity squashing
        effective_similarity = similarity ** 2

        total_weighted_score += base_weight * quality_weight * effective_similarity

    if total_possible_score == 0:
        return 0.0

    return round((total_weighted_score / total_possible_score) * 100, 2)
