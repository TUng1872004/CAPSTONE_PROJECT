from typing import Any, Optional
from uuid import uuid4, UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    BackgroundTasks
)
from pydantic import BaseModel, Field
from loguru import logger


from core.config.storage import minio_settings
from core.pipeline.tracker import ArtifactTracker
from core.storage import StorageClient
from core.dependencies.application import get_artifact_tracker, get_storage_client
from flow.video_processing import video_processing_flow

router = APIRouter(prefix="/uploads", tags=["uploads"])

class UploadResponse(BaseModel):
    """Response after successful upload."""
    run_id: str
    flow_run_id: str
    video_count: int
    video_names: list[str]
    status: str
    message: str
    tracking_url: Optional[str] = None




@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload videos and start processing",
    description="Upload one or more videos and automatically trigger the Prefect processing pipeline"
)
async def upload_videos(
    background_tasks: BackgroundTasks,
    request_files: list[tuple[str,str]],
) -> UploadResponse:
    
    

    logger.info(f"Calling video_processing_flow directly")
    run_id = str(uuid4())



    def run_flow_sync():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                video_processing_flow(
                    video_files=request_files,
                    run_id=run_id,
                )
            )
            logger.info(f"Flow completed: {result}")
        except Exception as e:
            logger.exception(f"Flow failed: {e}")
        finally:
            loop.close()
    
    background_tasks.add_task(run_flow_sync)

    return UploadResponse(
        run_id=run_id,
        flow_run_id=run_id,  
        video_count=len(request_files),
        video_names=[f[1] or "unknown" for f in request_files],
        status="RUNNING",
        message=f"Processing started directly for {len(request_files)} video(s)",
        tracking_url=f"/api/management/videos/{run_id}/status"
    )





    
