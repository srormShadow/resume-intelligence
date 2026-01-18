# One responsibility:

# Given JD concepts and Resume concepts, decide:

# what matches
# what partially matches
# what is missing

# It uses:
# embedder.py → vectors
# similarity.py → cosine similarity math

# ≥ 0.75  → MATCHED
# 0.55–0.75 → PARTIAL
# < 0.55 → MISSING


# OUTPUT : 
# {
#   "matched": [
#     {
#       "jd_concept": "api integration",
#       "jd_type": "skill",
#       "score": 0.86,
#       "matched_resume_concept": "integrate secure rest apis"
#     }
#   ],
#   "partial": [
#     {
#       "jd_concept": "ci cd pipeline",
#       "jd_type": "tool",
#       "score": 0.63,
#       "matched_resume_concept": "ci cd"
#     }
#   ],
#   "missing": [
#     {
#       "jd_concept": "cloud platform",
#       "jd_type": "tool",
#       "score": 0.21,
#       "matched_resume_concept": "android studio"
#     }
#   ]
# }


from typing import Dict, List

import numpy as np

from resume_intelligence.core.semantics.concept import Concept
from resume_intelligence.core.matching.embedder import ConceptEmbedder
from resume_intelligence.core.matching.similarity import similarity_matrix

from resume_intelligence.core.semantics.concept import ConceptType

TYPE_COMPATIBILITY = {
    ConceptType.SKILL: {ConceptType.SKILL, ConceptType.PRACTICE},
    ConceptType.TOOL: {ConceptType.TOOL},
    ConceptType.PRACTICE: {ConceptType.PRACTICE, ConceptType.SKILL},
    ConceptType.ROLE_CONTEXT: {ConceptType.ROLE_CONTEXT},
}



# Thresholds for semantic matching
STRONG_MATCH_THRESHOLD = 0.75
PARTIAL_MATCH_THRESHOLD = 0.55


class ConceptMatcher:
    """
    Matches JD concepts against resume concepts using semantic similarity.
    """

    def __init__(self, embedder: ConceptEmbedder | None = None):
        self._embedder = embedder or ConceptEmbedder()

    def match(
        self,
        jd_concepts: List[Concept],
        resume_concepts: List[Concept],
    ) -> Dict[str, List[Dict]]:
        """
        Perform semantic matching between JD and resume concepts.

        Returns:
            Dictionary with matched, partial, and missing concepts.
        """

        if not jd_concepts:
            return {"matched": [], "partial": [], "missing": []}

        jd_texts = [c.text for c in jd_concepts]
        resume_texts = [c.text for c in resume_concepts]

        jd_vectors = self._embedder.embed_texts(jd_texts)
        resume_vectors = self._embedder.embed_texts(resume_texts)

        sim_matrix = similarity_matrix(jd_vectors, resume_vectors)

        results = {
            "matched": [],
            "partial": [],
            "missing": [],
        }

        for i, jd_concept in enumerate(jd_concepts):
            if resume_vectors:
                similarities = sim_matrix[i]
                best_idx = int(np.argmax(similarities))
                best_score = float(similarities[best_idx])
                best_resume_text = resume_texts[best_idx]
            else:
                best_score = 0.0
                best_resume_text = None

            record = {
                "jd_concept": jd_concept.text,
                "jd_type": jd_concept.type,
                "score": round(best_score, 2),
                "matched_resume_concept": best_resume_text,
            }

            if best_score >= STRONG_MATCH_THRESHOLD:
                results["matched"].append(record)
            elif best_score >= PARTIAL_MATCH_THRESHOLD:
                results["partial"].append(record)
            else:
                results["missing"].append(record)

        return results

