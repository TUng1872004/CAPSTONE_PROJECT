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
from service_asr.core.api import router
from service_asr.core.config import asr_service_config
from service_asr.core.dependencies import get_service
from service_asr.core.lifespan import lifespan

app = FastAPI(
    title="ASR Service",
    description="Automatic speech recognition powered by Chunkformer",
    version=asr_service_config.service_version,
    lifespan=lifespan,
)

app.include_router(router, prefix="/asr", tags=["asr"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": asr_service_config.service_name}


@app.get("/metrics")
async def metrics(service=Depends(get_service)) -> Response:
    service.update_system_metrics()
    return Response(
        content=service.metrics.get_metrics(),
        media_type=service.metrics.get_content_type(),
    )


if __name__ == "__main__":
    logger.info(
        "starting_asr_service",
        host=asr_service_config.host,
        port=asr_service_config.port,
        version=asr_service_config.service_version,
    )
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=asr_service_config.port,
        reload=True,
        log_level="info",
    )
