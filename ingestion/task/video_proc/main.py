from __future__ import annotations
from typing import AsyncIterator, BinaryIO, cast, Callable
from pathlib import Path
from pydantic import BaseModel
from fastapi import UploadFile

from prefect import task
from loguru import logger
from core.pipeline.base_task import BaseTask
from core.artifact.persist import  ArtifactPersistentVisitor
from core.artifact.schema import VideoArtifact
from core.clients.base import BaseServiceClient, BaseMilvusClient
from .config import VideoIngestionSettings
from .util import get_video_metadata, valid_video_files
from core.management.progress import ProcessingStage
from core.app_state import AppState

# tracker = AppState().progress_tracker

class VideoInput(BaseModel):
    files: list[tuple[str,str]]
    user_id: str



def extract_extension(s3_link:str) ->str:
    return s3_link.split('.')[-1]

class VideoIngestionTask(BaseTask[VideoInput, VideoArtifact, VideoIngestionSettings]):
    def __init__(
        self, 
        artifact_visitor: ArtifactPersistentVisitor,
        config: VideoIngestionSettings
    ):
        super().__init__(
            name=VideoIngestionTask.__name__,
            visitor=artifact_visitor,
            config=config
        )
        

    async def preprocess(
        self, input_data: VideoInput
    ) -> VideoInput:
        return input_data

    async def execute(
        self,
        input_data: VideoInput,
        client: BaseServiceClient | None | BaseMilvusClient
    ) -> AsyncIterator[tuple[VideoArtifact, bool]]:
        user_bucket_name = input_data.user_id



        for video_info in input_data.files:

            video_id, video_s3_path = video_info
            video_extension = extract_extension(video_s3_path)
            

            try:
                video_artifact = VideoArtifact(
                    artifact_type=VideoArtifact.__name__,
                    task_name=self.name,
                    video_id=video_id,
                    video_extension=video_extension,
                    video_minio_url=video_s3_path,
                    user_bucket=user_bucket_name
                )
                
                exists = await video_artifact.accept_check_exist(self.visitor)
                print(f"Exists: {exists}")
                video_id = video_artifact.artifact_id
                
                yield video_artifact, exists
            except Exception as e:
                logger.exception(f" Failed to process video {video_s3_path}: {e}")
                continue

    async def postprocess(self, output_data: tuple[VideoArtifact, BinaryIO | None]) -> VideoArtifact:
        artifact, data = output_data
        if data:
            return artifact
        await artifact.accept_upload(self.visitor)
        return artifact


