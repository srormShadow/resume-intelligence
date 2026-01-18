# Convert text (concepts) → numerical vectors (embeddings)

# INPUT : ["api integration", "unit testing"]
# OUTPUT : [[0.12, -0.44, ..., 0.33],[-0.18, 0.91, ..., -0.05]]

from typing import List

from sentence_transformers import SentenceTransformer

class ConceptEmbedder:
    """
    Converts text concepts into semantic vector embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load model once
        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts into semantic vectors.

        Args:
            texts: List of concept strings

        Returns:
            List of embedding vectors (list of floats)
        """
        if not texts:
            return []

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Convert numpy arrays to Python lists for portability
        return embeddings.tolist()
