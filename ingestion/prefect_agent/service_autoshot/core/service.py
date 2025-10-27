from __future__ import annotations

from loguru import logger

from shared.config import LogConfig
from shared.service import BaseService
from service_autoshot.core.config import AutoshotConfig
from service_autoshot.schema import AutoShotRequest, AutoShotResponse


class AutoshotService(BaseService[AutoShotRequest, AutoShotResponse]):
    """Thin wrapper around the shared BaseService for autoshot models."""

    def __init__(self, service_config: AutoshotConfig, log_config: LogConfig) -> None:
        super().__init__(service_config=service_config, log_config=log_config)
        logger.info(
            f"Autoshot Service Initialize with service name: {service_config.service_name} with version {service_config.service_version}",
            service=service_config.service_name,
            version=service_config.service_version,
        )

    def get_available_models(self) -> list[str]:
        registered = super().get_available_models()
        return [model for model in registered if model == "autoshot"]
