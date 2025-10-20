from __future__ import annotations

from loguru import logger

from shared.config import LogConfig
from shared.service import BaseService
from service_asr.core.config import ASRServiceConfig
from service_asr.core.schema import ASRInferenceRequest, ASRInferenceResponse


class ASRService(BaseService[ASRInferenceRequest, ASRInferenceResponse]):
    """Thin wrapper around the shared BaseService for ASR models."""

    def __init__(self, service_config: ASRServiceConfig, log_config: LogConfig) -> None:
        super().__init__(service_config=service_config, log_config=log_config)
        self._service_config = service_config
        logger.info(
            "asr_service_initialized",
            service=service_config.service_name,
            version=service_config.service_version,
        )

    def get_available_models(self) -> list[str]:
        registered = super().get_available_models()
        return [model for model in registered if model == "chunkformer"]
