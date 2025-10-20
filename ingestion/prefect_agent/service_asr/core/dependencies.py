from fastapi import Request

from shared.config import LogConfig
from service_asr.core.config import ASRServiceConfig
from service_asr.core.service import ASRService


def initialize_service(service_config: ASRServiceConfig, log_config: LogConfig) -> ASRService:
    return ASRService(service_config=service_config, log_config=log_config)


def get_service(request: Request) -> ASRService:
    return request.app.state.service
