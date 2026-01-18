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

from resume_intelligence.core.semantics.concept import Concept, ConceptType
from resume_intelligence.core.matching.embedder import ConceptEmbedder
from resume_intelligence.core.matching.similarity import similarity_matrix


# Thresholds for semantic matching
STRONG_MATCH_THRESHOLD = 0.75
PARTIAL_MATCH_THRESHOLD = 0.55


# -------------------------
# Concept type compatibility
# -------------------------
TYPE_COMPATIBILITY = {
    ConceptType.SKILL: {ConceptType.SKILL, ConceptType.PRACTICE},
    ConceptType.TOOL: {ConceptType.TOOL},
    ConceptType.PRACTICE: {ConceptType.PRACTICE, ConceptType.SKILL},
    ConceptType.ROLE_CONTEXT: {ConceptType.ROLE_CONTEXT},
}


class ConceptMatcher:
    """
    Matches JD concepts against resume concepts using
    type-aware semantic similarity.
    """

    def __init__(self, embedder: ConceptEmbedder | None = None):
        self._embedder = embedder or ConceptEmbedder()

    def match(
        self,
        jd_concepts: List[Concept],
        resume_concepts: List[Concept],
    ) -> Dict[str, List[Dict]]:

        if not jd_concepts:
            return {"matched": [], "partial": [], "missing": []}

        results = {
            "matched": [],
            "partial": [],
            "missing": [],
        }

        for jd_concept in jd_concepts:
            # 🔒 Filter resume concepts by compatible types
            allowed_types = TYPE_COMPATIBILITY.get(jd_concept.type, set())
            filtered_resume = [
                rc for rc in resume_concepts if rc.type in allowed_types
            ]

            if not filtered_resume:
                results["missing"].append({
                    "jd_concept": jd_concept.text,
                    "jd_type": jd_concept.type,
                    "score": 0.0,
                    "matched_resume_concept": None,
                })
                continue

            jd_vector = self._embedder.embed_texts([jd_concept.text])[0]
            resume_texts = [rc.text for rc in filtered_resume]
            resume_vectors = self._embedder.embed_texts(resume_texts)

            similarities = similarity_matrix(
                [jd_vector],
                resume_vectors,
            )[0]

            best_idx = int(np.argmax(similarities))
            best_score = float(similarities[best_idx])
            best_resume_text = resume_texts[best_idx]

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
