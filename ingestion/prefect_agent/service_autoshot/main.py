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
from service_autoshot.core.api import router
from service_autoshot.core.config import autoshot_config
from service_autoshot.core.dependency import get_service
from service_autoshot.core.lifespan import lifespan


app = FastAPI(
    title="Autoshot Service",
    description="Automatic shot boundary detection via TransNetV2",
    version=autoshot_config.service_version,
    lifespan=lifespan,
)

app.include_router(router, prefix="/autoshot", tags=["autoshot"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": autoshot_config.service_name}


@app.get("/metrics")
async def metrics(service=Depends(get_service)) -> Response:
    service.update_system_metrics()
    return Response(
        content=service.metrics.get_metrics(),
        media_type=service.metrics.get_content_type(),
    )


if __name__ == "__main__":
    logger.info(
        "starting_autoshot_service",
        host=autoshot_config.host,
        port=autoshot_config.port,
        version=autoshot_config.service_version,
    )
    uvicorn.run(
        "service_autoshot.main:app",
        host='0.0.0.0',
        port=autoshot_config.port,
        reload=True,
        log_level="info",
    )

