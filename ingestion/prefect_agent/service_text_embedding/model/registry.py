"""Import model handlers to ensure registration with the shared registry."""

from service_text_embedding.model.mmbert import MMBERTHandler  # noqa: F401
from service_text_embedding.model.sentence_transformers import SentenceTransformerHandler  # noqa: F401

AVAILABLE_TEXT_MODELS = [
    "sentence_embedding",
    "mmbert",
]

__all__ = [
    "AVAILABLE_TEXT_MODELS",
    "MMBERTHandler",
    "SentenceTransformerHandler",
]
