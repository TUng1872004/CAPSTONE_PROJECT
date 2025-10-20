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
    files: list[UploadFile]
    user_id: str


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
        
        logger.info(f"Preprocessing video ingestion")
        if not input_data.files:
            raise ValueError(f"No videos provided in the run context") 
        valid_files = []
        for video in input_data.files:
            if not video.filename:
                raise ValueError(f"Invalid video file: {video}")
            if not valid_video_files(video):
                logger.warning(f"File: {video.filename} is not a video, not included in the processing")
            valid_files.append(video)
        
        input_data.files = valid_files

        print(f"{input_data=}")
        return input_data

    async def execute(
        self,
        input_data: VideoInput,
        client: BaseServiceClient | None | BaseMilvusClient
    ) -> AsyncIterator[tuple[VideoArtifact, BinaryIO | None]]:
        user_bucket_name = input_data.user_id
        for video_upload in input_data.files:
            try:
                video_filename = cast(str, video_upload.filename)
                video_name = Path(video_filename).stem
                metadata = get_video_metadata(video_filename=video_filename, file=video_upload.file)
                content_type = cast(str, video_upload.content_type)
                video_artifact = VideoArtifact(
                    extension=metadata['extension'],
                    video_name=video_name,
                    content_type=content_type,
                    metadata=metadata,
                    user_bucket=user_bucket_name,
                    task_name=self.name,
                    artifact_type=VideoArtifact.__name__
                )
                
                exists = await video_artifact.accept_check_exist(self.visitor)
                print(f"Exists: {exists}")


                video_id = video_artifact.artifact_id
                

                if exists:
                    yield video_artifact, None
                   
                else:
                    video_upload.file.seek(0)
                    yield video_artifact, video_upload.file
            except Exception as e:
                logger.exception(f" Failed to process video {video_upload.filename}: {e}")
                continue

    async def postprocess(self, output_data: tuple[VideoArtifact, BinaryIO | None]) -> VideoArtifact:
        artifact, data = output_data
        if data is  None:
            return artifact

        await artifact.accept_upload(self.visitor, data)
        return artifact


