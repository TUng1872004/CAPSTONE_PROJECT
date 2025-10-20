from typing import Any, Optional
from uuid import UUID
from fastapi import HTTPException, APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from core.management.cleanup import ArtifactDeleter, DeletionResult
from core.management.milvus_manager import MilvusManager, MilvusDeletionOutcome
from core.management.status import VideoStatusManager, VideoStatusInfo
from core.dependencies.application import get_artifact_deleter, get_artifact_tracker, get_storage_client
from core.pipeline.tracker import ArtifactTracker
from core.storage import StorageClient
from core.lifespan import AppState
from core.config.logging import run_logger

router = APIRouter(prefix='/management', tags=["management"])


class DeletionResponse(BaseModel):
    """Response model for deletion operations."""
    success: bool
    video_id: str
    message: str
    deleted_artifacts: int
    deleted_lineage: int
    deleted_minio_objects: int


class MilvusDeletionResponse(BaseModel):
    success: bool
    user_id: str
    related_video_id: str
    total_deleted: int
    per_collection_deleted: dict[str, int]
    errors: list[str] = Field(default_factory=list)

@router.delete(
    "/videos/{video_id}",
    response_model=DeletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete video and all derived artifacts",
    description="Cascading deletion of video and all derived artifacts (segments, transcripts, embeddings, etc.)"
)
async def delete_video(
    video_id: str,
    deleter: ArtifactDeleter = Depends(get_artifact_deleter)
) -> DeletionResponse:
    result: DeletionResult = await deleter.delete_video_cascade(video_id)
    return DeletionResponse(
        success=result.success,
        video_id=result.video_id,
        message=f"Successfully deleted video '{video_id}' and {result.deleted_artifacts} artifacts",
        deleted_artifacts=result.deleted_artifacts,
        deleted_lineage=result.deleted_lineage,
        deleted_minio_objects=result.deleted_minio_objects,
    )


@router.delete(
    "/videos/{video_id}/stages/{artifact_type}",
    response_model=DeletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete artifacts from a specific stage",
    description="Delete all artifacts of a specific type/stage for a video, including descendants"
)
async def delete_video_stage(
    video_id: str,
    artifact_type: str,
    deleter: ArtifactDeleter = Depends(get_artifact_deleter)
) -> DeletionResponse:
    """Delete all artifacts of a specific stage/type for a video."""
    try:
        result: DeletionResult = await deleter.delete_stage_artifacts(
            video_id=video_id,
            artifact_type=artifact_type
        )
        return DeletionResponse(
            success=result.success,
            video_id=result.video_id,
            message=f"Successfully deleted {result.deleted_artifacts} artifacts of type '{artifact_type}'",
            deleted_artifacts=result.deleted_artifacts,
            deleted_lineage=result.deleted_lineage,
            deleted_minio_objects=result.deleted_minio_objects,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete stage artifacts: {str(e)}"
        )


@router.post(
    "/videos/batch-delete",
    response_model=list[DeletionResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete multiple videos in batch"
)
async def batch_delete_videos(
    video_ids: list[str],
    deleter: ArtifactDeleter = Depends(get_artifact_deleter)
) -> list[DeletionResponse]:
    results = []
    
    for video_id in video_ids:
        try:
            result = await deleter.delete_video_cascade(video_id)
            results.append(
                DeletionResponse(
                    success=result.success,
                    video_id=result.video_id,
                    message=f"Deleted {result.deleted_artifacts} artifacts",
                    deleted_artifacts=result.deleted_artifacts,
                    deleted_lineage=result.deleted_lineage,
                    deleted_minio_objects=result.deleted_minio_objects,
                )
            )
        except Exception as e:
            results.append(
                DeletionResponse(
                    success=False,
                    video_id=video_id,
                    message=f"Failed: {str(e)}",
                    deleted_artifacts=0,
                    deleted_lineage=0,
                    deleted_minio_objects=0,
                )
            )
    
    return results


@router.delete(
    "/milvus/users/{user_id}/videos/{related_video_id}",
    response_model=MilvusDeletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Milvus records across all collections for a video",
    description=(
        "Dynamically delete all Milvus records referencing the given related_video_id "
        "across every registered collection scoped by user_id (_{user_id}_<collection>)."
    ),
)
async def delete_milvus_by_video(
    user_id: str,
    related_video_id: str,
) -> MilvusDeletionResponse:
    manager = MilvusManager()
    outcome: MilvusDeletionOutcome = await manager.delete_by_related_video_id(user_id, related_video_id)
    return MilvusDeletionResponse(
        success=outcome.success,
        user_id=user_id,
        related_video_id=related_video_id,
        total_deleted=outcome.total_deleted,
        per_collection_deleted=outcome.per_collection_deleted,
        errors=outcome.errors,
    )


@router.get(
    "/videos/{video_id}/status",
    response_model=VideoStatusInfo,
    status_code=status.HTTP_200_OK,
    summary="Get video processing status",
    description="Retrieve detailed processing status for a video by ID or name"
)
async def get_video_status(
    video_id: str,
    tracker: ArtifactTracker = Depends(get_artifact_tracker),
    storage: StorageClient = Depends(get_storage_client)
) -> VideoStatusInfo:
    """Get the current processing status of a video."""
    status_manager = VideoStatusManager(tracker, storage)
    
    try:
        video_status = await status_manager.get_video_status(video_id)
        if video_status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video '{video_id}' not found"
            )
        return video_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}"
        )
    



# @router.websocket("/ws/progress/{video_id}")
# async def websocket_progress(websocket: WebSocket, video_id: str):
#     await websocket.accept()
#     try:
#         while True:
#             progress: Optional[VideoProgress] = app.state.progress_tracker.get_progress(video_id)  # type: ignore
#             if progress:
#                 data = {
#                     "video_id": progress.video_id,
#                     "overall_percentage": progress.overall_percentage,
#                     "current_stage": progress.current_stage.value if progress.current_stage else None,
#                     "status": progress.status,
#                     "stages": {
#                         stage.value: {
#                             "total_items": sp.total_items,
#                             "completed_items": sp.completed_items,
#                             "percentage": sp.percentage,
#                             "details": sp.details,
#                         }
#                         for stage, sp in progress.stages.items()
#                     }
#                 }
#                 await websocket.send_text(json.dumps(data))
#             await asyncio.sleep(1)  # Poll every second
#     except WebSocketDisconnect:
#         run_logger.info(f"WebSocket disconnected for video_id: {video_id}")
