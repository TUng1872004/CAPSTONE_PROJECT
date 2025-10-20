from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from shared.config import LogConfig
from service_llm.core.config import llm_service_config
from service_llm.core.dependencies import initialize_service
from service_llm.model import registry as _  # noqa: F401 ensure handlers register
from shared.service_registry import ConsulServiceRegistry



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_llm_service")

    log_config = LogConfig(
        log_level=llm_service_config.log_level,
        log_format=llm_service_config.log_format,
        log_file=llm_service_config.log_file,
        log_rotation=llm_service_config.log_rotation,
        log_retention=llm_service_config.log_retention,
    ) 
    service = initialize_service(llm_service_config, log_config)
    app.state.service = service

    logger.info(
        "llm_service_ready",
        available_models=service.get_available_models(),
    )


    consul= ConsulServiceRegistry(
        host='consul',
        port=8500
    )
    await consul.register_service(
        service_name=llm_service_config.service_name,
        address=llm_service_config.host,
        port=llm_service_config.port,
        tags=['ml', 'gpu', 'llm'],
        health_check_url=f"http://{llm_service_config.host}:{llm_service_config.port}/health",
    )

    logger.info(f"✅ LLM service registered with Consul")
    logger.info(f"   Service: {llm_service_config.service_name}")
    logger.info(f"   Address: {llm_service_config.host}:{llm_service_config.port}")
    logger.info(f"   Health: http://{llm_service_config.host}:{llm_service_config.port}/health")


    try:
        yield
    finally:
        logger.info("stopping_llm_service")
        if service.loaded_model is not None:
            await service.unload_model(cleanup_memory=True)
        logger.info("llm_service_shutdown_complete")
