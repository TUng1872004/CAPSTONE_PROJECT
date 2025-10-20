from pydantic import Field

from shared.config import ServiceConfig, LogLevel


class TextEmbeddingConfig(ServiceConfig):
    """Runtime configuration for the text embedding service."""

    sentence_transformer_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model name for SentenceTransformer backbone",
    )
    sentence_transformer_batch_size: int = Field(
        default=32,
        ge=1,
        description="Default batch size for SentenceTransformer inference",
    )

    mmbert_model_name: str | None = Field(
        default=None,
        description="Optional Hugging Face identifier for mmBERT checkpoint",
    )
    mmbert_max_length: int = Field(default=512, ge=8, description="Maximum token length for mmBERT")
    mmbert_batch_size: int = Field(default=8, ge=1, description="Default batch size for mmBERT inference")

    log_level: LogLevel = Field(default=LogLevel.DEBUG)
    log_format: str = Field(default="console")
    log_retention: str = Field(default="30 days")
    log_file: str = Field(default="./logs/app.log")
    log_rotation: str = Field(default="100 MB")


text_embedding_config = TextEmbeddingConfig()  # type: ignore[arg-type]
