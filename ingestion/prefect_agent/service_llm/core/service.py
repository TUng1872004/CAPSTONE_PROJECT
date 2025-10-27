from __future__ import annotations

from typing import Dict, Optional, cast

from loguru import logger

from shared.config import LogConfig
from shared.registry import BaseModelHandler
from shared.service import BaseService
from shared.schema import ModelInfo
from service_llm.core.config import LLMServiceConfig
from service_llm.schema import LLMRequest, LLMResponse


class LLMService(BaseService[LLMRequest, LLMResponse]):
    """Service wrapper exposing multimodal LLM handlers via the shared BaseService."""

    def __init__(self, service_config: LLMServiceConfig, log_config: LogConfig) -> None:
        super().__init__(service_config=service_config, log_config=log_config)
        self._service_config = service_config
        self._model_cache: Dict[str, BaseModelHandler[LLMRequest, LLMResponse]] = {}
        logger.info(
            "llm_service_initialized",
            service=service_config.service_name,
            version=service_config.service_version,
        )

    def get_available_models(self) -> list[str]:
        registered = super().get_available_models()
        enabled: list[str] = []

        if self._service_config.gemini_api_key and "gemini_api" in registered:
            enabled.append("gemini_api")

        if self._service_config.openrouter_api_key and "openrouter_api" in registered:
            enabled.append("openrouter_api")



        return enabled
