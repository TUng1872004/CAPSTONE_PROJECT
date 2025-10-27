from __future__ import annotations

from typing import Dict, Optional, cast

from loguru import logger

from shared.config import LogConfig
from shared.registry import BaseModelHandler
from shared.service import BaseService
from shared.schema import ModelInfo
from service_text_embedding.core.config import TextEmbeddingConfig
from service_text_embedding.schema import TextEmbeddingRequest, TextEmbeddingResponse


class TextEmbeddingService(BaseService[TextEmbeddingRequest, TextEmbeddingResponse]):
    """Service wrapper that exposes text embedding handlers via the shared BaseService."""

    def __init__(self, service_config: TextEmbeddingConfig, log_config: LogConfig) -> None:
        super().__init__(service_config=service_config, log_config=log_config)
        self._service_config = service_config
        self._model_cache: Dict[str, BaseModelHandler[TextEmbeddingRequest, TextEmbeddingResponse]] = {}
        logger.info(
            "text_embedding_service_initialized",
            service=service_config.service_name,
            version=service_config.service_version,
        )

    def get_available_models(self) -> list[str]:
        registered = super().get_available_models()
        enabled: list[str] = []

        if self._service_config.sentence_transformer_model and "sentence_embedding" in registered:
            enabled.append("sentence_embedding")

        if self._service_config.mmbert_model_name and "mmbert" in registered:
            enabled.append("mmbert")

        return enabled


