from datetime import datetime
from enum import Enum
from typing import Any, Optional, Type

from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from task.common.util import parse_s3_url
from core.pipeline.tracker import ArtifactTracker, ArtifactSchema
from core.storage import StorageClient

from core.artifact.schema import VideoArtifact, AutoshotArtifact, ASRArtifact, ImageArtifact, SegmentCaptionArtifact, ImageCaptionArtifact, ImageEmbeddingArtifact, TextCaptionEmbeddingArtifact, TextCapSegmentEmbedArtifact , BaseArtifact


       



class VideoStatusInfo(BaseModel):
    video_id: str
    video_name: str
    stages_completed: list[str] = Field(default_factory=list)
    progress_percentage: float = Field(ge=0,le=100)
    metadata: dict


class VideoStatusManager:
    def __init__(self, tracker: ArtifactTracker, storage: StorageClient):
        self.tracker = tracker
        self.storage = storage
    
    async def get_all_descendants(
        self,
        session: AsyncSession,
        parent_id: str,
        visited: dict[str, ArtifactSchema] | None = None,
    ) -> dict[str, ArtifactSchema]:
        """
        Returns a dict mapping artifact_id -> ArtifactSchema object
        for the root and all descendants.
        """
        if visited is None:
            visited = {}

        if parent_id in visited:
            return visited

        parent = await session.get(ArtifactSchema, parent_id)
        if not parent:
            return visited  

        visited[parent_id] = parent

        query = select(ArtifactSchema).where(
            ArtifactSchema.parent_artifact_id == parent_id
        )
        result = await session.execute(query)
        children = result.scalars().all()

        for child in children:
            await self.get_all_descendants(session, child.artifact_id, visited)

        return visited
    
    def analyze_artifacts(
        self,
        session: AsyncSession,
        video_artifact: ArtifactSchema,
        descendants: list[ArtifactSchema],
    ) -> VideoStatusInfo:
        _, video_name = parse_s3_url(video_artifact.minio_url)
        artifact_counts = {}
        for artifact in descendants:
            artifact_type = artifact.artifact_type
            artifact_counts[artifact_type] = artifact_counts.get(artifact_type, 0) + 1
        
        completed_stages = []

        STAGES: list[Type[BaseArtifact]] = [
            AutoshotArtifact, ASRArtifact, ImageArtifact, SegmentCaptionArtifact, ImageCaptionArtifact, ImageEmbeddingArtifact, TextCaptionEmbeddingArtifact, TextCapSegmentEmbedArtifact 
        ]
        for stage in STAGES:
            if artifact_counts.get(stage.__name__, 0) > 0:
                completed_stages.append(stage.__name__)
        
        total_stages = len(STAGES)
        completed_count = len(completed_stages)
        progress = (completed_count / total_stages) * 100

        latest_update = video_artifact.created_at
        for artifact in descendants:
            if artifact.created_at > latest_update:
                latest_update = artifact.created_at
        
        return VideoStatusInfo(
            video_id=video_artifact.artifact_id,
            video_name=video_name,
            stages_completed=completed_stages,
            progress_percentage=round(progress, 2),
            metadata={
                "artifact_counts": artifact_counts,
                "minio_url": video_artifact.minio_url
            }
        )

    
    
    async def get_video_status(self, video_id: str) -> Optional[VideoStatusInfo]:
        async with self.tracker.get_session() as session:
            video_query = select(ArtifactSchema).where(
                ArtifactSchema.artifact_id == video_id
            )
            result = await session.execute(video_query)
            video_artifact = result.scalar_one_or_none()

            if not video_artifact:
                return None
            

            descendent_dict = await self.get_all_descendants(parent_id=video_id, session=session)
            descendent_results = list(descendent_dict.values()) 
            _, video_name = parse_s3_url(video_artifact.minio_url)
            artifact_counts = {}
            for artifact in descendent_results:
                artifact_type = artifact.artifact_type
                artifact_counts[artifact_type] = artifact_counts.get(artifact_type, 0) + 1
            
            completed_stages = []

            STAGES: list[Type[BaseArtifact]] = [
                AutoshotArtifact, ASRArtifact, ImageArtifact, SegmentCaptionArtifact, ImageCaptionArtifact, ImageEmbeddingArtifact, TextCaptionEmbeddingArtifact, TextCapSegmentEmbedArtifact 
            ]
            for stage in STAGES:
                if artifact_counts.get(stage.__name__, 0) > 0:
                    completed_stages.append(stage.__name__)
            
            total_stages = len(STAGES)
            completed_count = len(completed_stages)
            progress = (completed_count / total_stages) * 100

            latest_update = video_artifact.created_at
            for artifact in descendent_results:
                if artifact.created_at > latest_update:
                    latest_update = artifact.created_at
            
            return VideoStatusInfo(
                video_id=video_artifact.artifact_id,
                video_name=video_name,
                stages_completed=completed_stages,
                progress_percentage=round(progress, 2),
                metadata={
                    "artifact_counts": artifact_counts,
                    "minio_url": video_artifact.minio_url
                }
            )
            
        
