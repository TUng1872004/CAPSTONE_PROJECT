from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from shared.config import LogConfig
from service_asr.core.config import asr_service_config
from service_asr.core.dependencies import initialize_service
from service_asr.model import registries as _  


from shared.service_registry import ConsulServiceRegistry

@asynccontextmanager
async def lifespan(app: FastAPI):


    logger.info("starting_asr_service")

    log_config = LogConfig(
        log_level=asr_service_config.log_level,
        log_format=asr_service_config.log_format,
        log_file=asr_service_config.log_file,
        log_rotation=asr_service_config.log_rotation,
        log_retention=asr_service_config.log_retention,
    ) 
    service = initialize_service(asr_service_config, log_config)
    app.state.service = service

    logger.info(
        "asr_service_ready",
        available_models=service.get_available_models(),
    )

    consul= ConsulServiceRegistry(
        host='consul',
        port=8500
    )
    logger.info(f"   Address: {asr_service_config.host}:{asr_service_config.port}")
    await consul.register_service(
        service_name=asr_service_config.service_name,
        address=asr_service_config.host,
        port=asr_service_config.port,
        tags=['ml', 'gpu', 'asr'],
        health_check_url=f"http://{asr_service_config.host}:{asr_service_config.port}/health",
    )

    logger.info(f"✅ Service registered with Consul")
    logger.info(f"   Service: {asr_service_config.service_name}")
    logger.info(f"   Address: {asr_service_config.host}:{asr_service_config.port}")
    logger.info(f"   Health: http://{asr_service_config.host}:{asr_service_config.port}/health")

    try:
        yield
    finally:
        logger.info("stopping_asr_service")
        if service.loaded_model is not None:
            await service.unload_model(cleanup_memory=True)
        logger.info("asr_service_shutdown_complete")
