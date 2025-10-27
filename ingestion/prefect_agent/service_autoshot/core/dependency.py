from fastapi import  Request
from service_autoshot.core.service import AutoshotService
from service_autoshot.core.config import AutoshotConfig
from shared.config import LogConfig

def initialize_service(service_config: AutoshotConfig, log_config: LogConfig) -> AutoshotService:
    return AutoshotService(
        service_config=service_config,
        log_config=log_config
    )


def get_service(request: Request) -> AutoshotService:
    return request.app.state.service