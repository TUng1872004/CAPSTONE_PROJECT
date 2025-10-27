import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import Response
from loguru import logger
import sys
import os
ROOT_DIR = os.path.abspath(
    os.path.join(
        __file__, '../..'
    )
)
print(ROOT_DIR)
sys.path.insert(0, ROOT_DIR)

from service_image_embedding.core.api import router
from service_image_embedding.core.config import image_embedding_config
from service_image_embedding.core.dependencies import get_service
from service_image_embedding.core.lifespan import lifespan

app = FastAPI(
    title="Image Embedding Service",
    description="Generate vector representations for images using configurable backends",
    version=image_embedding_config.service_version,
    lifespan=lifespan,
)

app.include_router(router, prefix="/image-embedding", tags=["image-embedding"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": image_embedding_config.service_name}


@app.get("/metrics")
async def metrics(service=Depends(get_service)) -> Response:
    service.update_system_metrics()
    return Response(
        content=service.metrics.get_metrics(),
        media_type=service.metrics.get_content_type(),
    )


if __name__ == "__main__":
    logger.info(
        f"starting image embedding service with {image_embedding_config.host}:{image_embedding_config.port}")
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=image_embedding_config.port,
        reload=True,
        log_level=image_embedding_config.log_level.value.lower(),
    )
