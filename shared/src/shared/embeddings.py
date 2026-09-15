from shared.logger import get_logger
from shared.singleton import Singleton

logger = get_logger("shared.embeddings")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    logger.warning("sentence-transformers not installed. Embedding functions will fail if invoked.")
    SentenceTransformer = None


class EmbeddingService(metaclass=Singleton):
    """Singleton service to load and execute sentence-transformer embeddings."""

    def __init__(self):
        if SentenceTransformer is None:
            raise RuntimeError(
                "Cannot initialize EmbeddingService because sentence-transformers is not installed."
            )
        model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        logger.info(f"Loading SentenceTransformer model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        logger.info("SentenceTransformer model loaded successfully.")

    def embed_text(self, text: str) -> list[float]:
        """Generate a 384-dimensional dense vector for the given text."""
        if not text:
            # Return empty or dummy vector if text is empty to avoid crashing
            return [0.0] * 384
        embedding = self.model.encode(text)
        return embedding.tolist()


def embed_text(text: str) -> list[float]:
    """Convenience helper to generate embeddings using the Singleton service."""
    return EmbeddingService().embed_text(text)
