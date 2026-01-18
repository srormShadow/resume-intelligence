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
    ConceptType.SKILL : 1.0,
    ConceptType.PRACTICE : 0.8,
    ConceptType.TOOL : 0.6,
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
    similarity_map = {}

    for bucket in ("matched", "partial", "missing"):
        for record in match_results[bucket]:
            similarity_map[record["jd_concept"]] = record["score"]

    total_weighted_score = 0.0
    total_possible_score = 0.0

    for concept in jd_concepts:
        similarity = similarity_map.get(concept.text, 0.0)
        confidence = concept.confidence
        type_weight = TYPE_WEIGHTS.get(concept.type, 0.5)

        weight = confidence * type_weight

        total_weighted_score += weight * similarity
        total_possible_score += weight

    if total_possible_score == 0:
        return 0.0

    return round((total_weighted_score / total_possible_score) * 100, 2)
