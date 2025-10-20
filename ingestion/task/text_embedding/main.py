from __future__ import annotations
from typing import Literal, cast, AsyncIterator, BinaryIO
from core.pipeline.base_task import BaseTask
from core.artifact.schema import TextCaptionEmbeddingArtifact, ImageCaptionArtifact, TextCapSegmentEmbedArtifact, SegmentCaptionArtifact
from core.artifact.persist import ArtifactPersistentVisitor
from core.clients.text_embed_client import  TextEmbeddingRequest, TextEmbeddingResponse
from task.common.util import fetch_object_from_s3
import asyncio
import json
from core.clients.base import BaseServiceClient, BaseMilvusClient
from pydantic import BaseModel
import io

from core.config.logging import run_logger

class TextEmbeddingSettings(BaseModel):
    model_name: str
    device: Literal['cuda', 'cpu'] 
    batch_size: int



class TextImageCaptionEmbeddingTask(BaseTask[
    list[ImageCaptionArtifact], TextCaptionEmbeddingArtifact, TextEmbeddingSettings
]):
    def __init__(
        self,
        artifact_visitor: ArtifactPersistentVisitor,
        config: TextEmbeddingSettings,
    ):
        super().__init__(
            name=TextImageCaptionEmbeddingTask.__name__,
            visitor=artifact_visitor,
            config=config
        )

    async def preprocess(
        self,
        input_data: list[ImageCaptionArtifact]
    ) -> list[TextCaptionEmbeddingArtifact]:
        result = []
        for img_artifact in input_data:
            text_embed_art = TextCaptionEmbeddingArtifact(
                frame_index=img_artifact.frame_index,
                related_video_name=img_artifact.related_video_name,
                image_caption_minio_url=img_artifact.minio_url_path,
                user_bucket=img_artifact.user_bucket,
                caption_id=img_artifact.artifact_id,
                artifact_type=TextCaptionEmbeddingArtifact.__name__,
                related_video_id=img_artifact.related_video_id
            )
            result.append(text_embed_art)
        return result
    

    async def execute(
        self,
        input_data: list[TextCaptionEmbeddingArtifact],
        client: BaseServiceClient | None | BaseMilvusClient
    ) -> AsyncIterator[tuple[TextCaptionEmbeddingArtifact, BinaryIO | None]]:
        assert client is not None, "The execution required client service"
        assert isinstance(client, BaseServiceClient)


        batch: list[TextCaptionEmbeddingArtifact] = []
        batches: list[list[TextCaptionEmbeddingArtifact]]  = []

        for artifact in input_data:
            exists = await artifact.accept_check_exist(self.visitor) 
            if exists:
                yield artifact, None
                continue
            
            batch.append(artifact)
            if len(batch) == self.config.batch_size:
                batches.append(batch[:])
                batch.clear()
                
        if batch:
            batches.append(batch[:])

        for batch in batches:
            caption_dict_path = await asyncio.gather(
                *[
                    fetch_object_from_s3(artifact.image_caption_minio_url, self.visitor.minio_client, suffix='.json') for artifact in batch
                ]
            )

            caption_str = [
                json.load(open(item_path, 'r', encoding='utf-8'))['caption'] for item_path in caption_dict_path
            ]

            request = TextEmbeddingRequest(
                texts=caption_str,
                metadata={}
            )

            

            response = await client.make_request(
                method='POST',
                endpoint=client.inference_endpoint,
                request_data=request
            )
            
            parsed = TextEmbeddingResponse.model_validate(response)
            embedding_captions = parsed.embeddings

            for artifact, embedding in zip(batch, embedding_captions):
                buffer = io.BytesIO(json.dumps(embedding).encode("utf-8"))
                buffer.seek(0)
                yield artifact, buffer
    
    async def postprocess(self, output_data: tuple[TextCaptionEmbeddingArtifact, BinaryIO | None]):
        artifact, data = output_data
        if data is None:
            return artifact
        await artifact.accept_upload(self.visitor, data)
        return artifact
    



class TextCaptionSegmentEmbeddingTask(
    BaseTask[
        list[SegmentCaptionArtifact], TextCapSegmentEmbedArtifact,TextEmbeddingSettings
    ]
):
    def __init__(
        self,
        artifact_visitor: ArtifactPersistentVisitor,
        config: TextEmbeddingSettings,
    ):
        super().__init__(
            name=TextCaptionSegmentEmbeddingTask.__name__,
            visitor=artifact_visitor,
            config=config
        )

    async def preprocess(
        self, 
        input_data:list[SegmentCaptionArtifact]
    ) -> list[TextCapSegmentEmbedArtifact]:
        result = []
        for seg_artifact in input_data:
            text_embed_art = TextCapSegmentEmbedArtifact(
                start_frame=seg_artifact.start_frame,
                end_frame=seg_artifact.end_frame,
                related_video_name=seg_artifact.related_video_name,
                related_segment_caption_url=seg_artifact.minio_url_path,
                user_bucket=seg_artifact.user_bucket,
                segment_cap_id=seg_artifact.artifact_id,
                artifact_type=TextCapSegmentEmbedArtifact.__name__,
                related_video_id=seg_artifact.related_video_id
            )
            result.append(text_embed_art)
        return result

    async def execute(
        self,
        input_data: list[TextCapSegmentEmbedArtifact],
        client: BaseServiceClient | None | BaseMilvusClient
    ) -> AsyncIterator[tuple[TextCapSegmentEmbedArtifact, BinaryIO | None]]:
        
        assert client is not None, "The execution required client service"
        assert isinstance(client, BaseServiceClient)


        batch: list[TextCapSegmentEmbedArtifact] = []
        batches: list[list[TextCapSegmentEmbedArtifact]]  = []

        for artifact in input_data:
            exists = await artifact.accept_check_exist(self.visitor) 
            if exists:
                yield artifact, None
                continue
            
            batch.append(artifact)
            if len(batch) == self.config.batch_size:
                batches.append(batch[:])
                batch.clear()
                
        if batch:
            batches.append(batch[:])

        for batch in batches:
            caption_dict_path = await asyncio.gather(
                *[
                    fetch_object_from_s3(artifact.related_segment_caption_url, self.visitor.minio_client, suffix='.json') for artifact in batch
                ]
            )

            caption_str = [
                json.load(open(item_path, 'r', encoding='utf-8'))['caption'] for item_path in caption_dict_path
            ]

            request = TextEmbeddingRequest(
                texts=caption_str,
                metadata={}
            )
            run_logger.debug(f"Request text embed: {request=}")
            run_logger.debug(f"Len caption: {len(caption_str)=}")
            response = await client.make_request(
                method='POST',
                endpoint=client.inference_endpoint,
                request_data=request
            )
            run_logger.debug(f"response text embed: {response=}")
            parsed = TextEmbeddingResponse.model_validate(response)
            embedding_captions = parsed.embeddings

            for artifact, embedding in zip(batch, embedding_captions):
                buffer = io.BytesIO(json.dumps(embedding).encode("utf-8"))
                buffer.seek(0)
                yield artifact, buffer

    async def postprocess(self, output_data: tuple[TextCapSegmentEmbedArtifact, BinaryIO | None]):
        artifact, data = output_data
        if data is None:
            return artifact
        await artifact.accept_upload(self.visitor, data)
        return artifact

