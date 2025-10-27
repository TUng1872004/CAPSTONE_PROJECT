from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from shared.config import LogConfig
from service_text_embedding.core.config import text_embedding_config
from service_text_embedding.core.dependencies import initialize_service
from service_text_embedding.model import registry as _  # noqa: F401 ensure handler registration
from shared.service_registry import ConsulServiceRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting text embedding service")

    log_config = LogConfig(
        log_file=text_embedding_config.log_file,
        log_level=text_embedding_config.log_level,
        log_format=text_embedding_config.log_format,
        log_rotation=text_embedding_config.log_rotation,
        log_retention=text_embedding_config.log_retention
    )
    service = initialize_service(text_embedding_config, log_config)
    app.state.service = service

    logger.info(
        "text_embedding_service_ready",
        available_models=service.get_available_models(),
    )

    consul= ConsulServiceRegistry(
        host='consul',
        port=8500
    )
    await consul.register_service(
        service_name=text_embedding_config.service_name,
        address=text_embedding_config.host,
        port=text_embedding_config.port,
        tags=['ml', 'gpu', 'text embedding'],
        health_check_url=f"http://{text_embedding_config.host}:{text_embedding_config.port}/health",
    )

    logger.info(f"✅ Text Embedding service registered with Consul")
    logger.info(f"   Service: {text_embedding_config.service_name}")
    logger.info(f"   Address: {text_embedding_config.host}:{text_embedding_config.port}")
    logger.info(f"   Health: http://{text_embedding_config.host}:{text_embedding_config.port}/health")


    try:
        yield
    finally:
        logger.info("stopping_text_embedding_service")
        if service.loaded_model is not None:
            await service.unload_model(cleanup_memory=True)
        logger.info("text_embedding_service_shutdown_complete")
