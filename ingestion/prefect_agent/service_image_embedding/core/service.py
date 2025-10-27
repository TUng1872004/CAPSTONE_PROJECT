from __future__ import annotations

from typing import Dict

from loguru import logger

from shared.config import LogConfig
from shared.registry import BaseModelHandler
from shared.service import BaseService
from service_image_embedding.core.config import ImageEmbeddingConfig


class ImageEmbeddingService(BaseService):
    """Service wrapper that exposes image embedding model handlers via the shared BaseService."""

    def __init__(self, service_config: ImageEmbeddingConfig, log_config: LogConfig) -> None:
        super().__init__(service_config=service_config, log_config=log_config)
        self._service_config = service_config
        self._model_instances: Dict[str, BaseModelHandler] = {}
        logger.info(
            "image_embedding_service_initialized",
            service=service_config.service_name,
            version=service_config.service_version,
        )
