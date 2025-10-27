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

from service_llm.core.api import router
from service_llm.core.config import llm_service_config
from service_llm.core.dependencies import get_service
from service_llm.core.lifespan import lifespan

app = FastAPI(
    title="LLM Service",
    description="Serve multimodal LLMs via shared service architecture",
    version=llm_service_config.service_version,
    lifespan=lifespan,
)

app.include_router(router, prefix="/llm", tags=["llm"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": llm_service_config.service_name}


@app.get("/metrics")
async def metrics(service=Depends(get_service)) -> Response:
    service.update_system_metrics()
    return Response(
        content=service.metrics.get_metrics(),
        media_type=service.metrics.get_content_type(),
    )


if __name__ == "__main__":
    logger.info(
        "starting_llm_service",
        host=llm_service_config.host,
        port=llm_service_config.port,
        version=llm_service_config.service_version,
    )
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=llm_service_config.port,
        reload=True,
        log_level="info",
    )
