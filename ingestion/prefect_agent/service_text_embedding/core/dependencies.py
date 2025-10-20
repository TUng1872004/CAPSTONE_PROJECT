from fastapi import Request

from shared.config import LogConfig
from service_text_embedding.core.config import TextEmbeddingConfig
from service_text_embedding.core.service import TextEmbeddingService


def initialize_service(service_config: TextEmbeddingConfig, log_config: LogConfig) -> TextEmbeddingService:
    return TextEmbeddingService(service_config=service_config, log_config=log_config)


def get_service(request: Request) -> TextEmbeddingService:
    return request.app.state.service
