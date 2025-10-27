from typing import Optional

from pydantic import Field

from shared.config import ServiceConfig, LogLevel




class ImageEmbeddingConfig(ServiceConfig):
    """Runtime configuration for the image embedding service."""

    # Model checkpoints
    beit3_model_checkpoint: str
    beit3_tokenizer_checkpoint: str
    open_clip_model_name: str
    open_clip_pretrained: str

    log_level: LogLevel = Field(default=LogLevel.DEBUG)
    log_format: str = Field(default="console")
    log_retention: str = Field(default="30 days")
    log_file: str = Field(default="./logs/app.log")
    log_rotation: str = Field(default="100 MB")




image_embedding_config = ImageEmbeddingConfig()  # type: ignore[arg-type]
