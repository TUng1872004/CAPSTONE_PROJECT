from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from service_autoshot.core.config import autoshot_config
from service_autoshot.core.dependency import initialize_service
from shared.config import LogConfig
from service_autoshot.model import registry as _  # noqa: F401 ensures model registration
from shared.service_registry import ConsulServiceRegistry



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle."""

    logger.info("starting_autoshot_service")
    logger.debug(f"Service config: {autoshot_config.model_dump(mode='json')}")
    log_config = LogConfig(
        log_level=autoshot_config.log_level,
        log_format=autoshot_config.log_format,
        log_file=autoshot_config.log_file,
        log_rotation=autoshot_config.log_rotation,
        log_retention=autoshot_config.log_retention,
    )
    logger.debug(f"Log config: {log_config.model_dump(mode='json')}")

    service = initialize_service(autoshot_config, log_config)
    app.state.service = service

    logger.info(
        "autoshot_service_ready",
        available_models=service.get_available_models(),
    )

    consul= ConsulServiceRegistry(
        host='consul',
        port=8500
    )
    await consul.register_service(
        service_name=autoshot_config.service_name,
        address=autoshot_config.host,
        port=autoshot_config.port,
        tags=['ml', 'gpu', 'asr'],
        health_check_url=f"http://{autoshot_config.host}:{autoshot_config.port}/health",
    )

    logger.info(f"✅ Autoshot service registered with Consul")
    logger.info(f"   Service: {autoshot_config.service_name}")
    logger.info(f"   Address: {autoshot_config.host}:{autoshot_config.port}")
    logger.info(f"   Health: http://{autoshot_config.host}:{autoshot_config.port}/health")


    try:
        yield
    finally:
        logger.info("stopping_autoshot_service")
        if service.loaded_model is not None:
            await service.unload_model(cleanup_memory=True)
        logger.info("autoshot_service_shutdown_complete")
