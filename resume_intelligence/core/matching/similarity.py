# Compute semantic similarity scores between vectors

#INPUT : jd_vectors = [
#     [0.6, 0.8],
#     [1.0, 0.0],
#   ]

# resume_vectors = [
#     [0.6, 0.8],
#     [0.0, 1.0],
# ]

# OUTPUT : similarity_matrix = [
#   [1.0, 0.8],
#   [0.6, 0.0],
# ]

# JD[0] strongly matches Resume[0]
# JD[1] weakly matches Resume[0]
# JD[1] does NOT match Resume[1]

from typing import List

import numpy as np


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two normalized vectors.

    Assumes both vectors are already L2-normalized.
    """
    a = np.array(vec_a)
    b = np.array(vec_b)

    # Since vectors are normalized, cosine similarity = dot product
    return float(np.dot(a, b))


def similarity_matrix(
    jd_vectors: List[List[float]],
    resume_vectors: List[List[float]],
) -> np.ndarray:
    """
    Compute cosine similarity matrix between JD and resume vectors.

    Returns:
        Matrix of shape (len(jd_vectors), len(resume_vectors))
    """
    if not jd_vectors or not resume_vectors:
        return np.zeros((len(jd_vectors), len(resume_vectors)))

    jd = np.array(jd_vectors)
    resume = np.array(resume_vectors)

    # Matrix multiplication gives all pairwise dot products
    return np.dot(jd, resume.T)
