from fastapi import Request

from shared.config import LogConfig
from service_image_embedding.core.config import ImageEmbeddingConfig
from service_image_embedding.core.service import ImageEmbeddingService


def initialize_service(service_config: ImageEmbeddingConfig, log_config: LogConfig) -> ImageEmbeddingService:
    return ImageEmbeddingService(service_config=service_config, log_config=log_config)


def get_service(request: Request) -> ImageEmbeddingService:
    return request.app.state.service
