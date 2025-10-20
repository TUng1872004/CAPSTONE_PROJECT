from fastapi import Request

from shared.config import LogConfig
from service_llm.core.config import LLMServiceConfig
from service_llm.core.service import LLMService


def initialize_service(service_config: LLMServiceConfig, log_config: LogConfig) -> LLMService:
    return LLMService(service_config=service_config, log_config=log_config)


def get_service(request: Request) -> LLMService:
    return request.app.state.service
