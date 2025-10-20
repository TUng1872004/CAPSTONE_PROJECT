from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from shared.config import LogConfig
from service_image_embedding.core.config import image_embedding_config
from service_image_embedding.core.dependencies import initialize_service
from service_image_embedding.model import registry as _
from shared.service_registry import ConsulServiceRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Image Embedding setup ")

    log_config = LogConfig(
        log_level=image_embedding_config.log_level,
        log_format=image_embedding_config.log_format,
        log_file=image_embedding_config.log_file,
        log_rotation=image_embedding_config.log_rotation,
        log_retention=image_embedding_config.log_retention,
    )  
    service = initialize_service(image_embedding_config, log_config)
    app.state.service = service

    logger.info(
        "Image embedding initialzied",
    )
    

    consul= ConsulServiceRegistry(
        host='consul',
        port=8500
    )
    await consul.register_service(
        service_name=image_embedding_config.service_name,
        address=image_embedding_config.host,
        port=image_embedding_config.port,
        tags=['ml', 'gpu', 'image', 'embedding'],
        health_check_url=f"http://{image_embedding_config.host}:{image_embedding_config.port}/health",
    )

    logger.info(f"✅ Image embedding service registered with Consul")
    logger.info(f"   Service: {image_embedding_config.service_name}")
    logger.info(f"   Address: {image_embedding_config.host}:{image_embedding_config.port}")
    logger.info(f"   Health: http://{image_embedding_config.host}:{image_embedding_config.port}/health")

    try:
        yield
    finally:
        logger.info("image_embedding_service_shutdown")
        if service.loaded_model is not None:
            await service.unload_model(cleanup_memory=True)
        logger.info("image_embedding_service_shutdown_complete")
