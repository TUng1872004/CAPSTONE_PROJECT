from __future__ import annotations
from typing import Literal, cast, AsyncIterator, BinaryIO
from core.clients.image_embed_client import ImageEmbeddingRequest, ImageEmbeddingResponse
from core.pipeline.base_task import BaseTask
from core.artifact.schema import ImageEmbeddingArtifact, ImageArtifact
from core.artifact.persist import ArtifactPersistentVisitor
from pydantic import BaseModel
from urllib.parse import urlparse
from pathlib import Path
import base64
import asyncio 
import io
import json
from task.common.util import fetch_object_from_s3
from core.clients.base import BaseServiceClient, BaseMilvusClient

class ImageEmbeddingSettings(BaseModel):
    model_name: str
    device: Literal['cuda', 'cpu']
    batch_size: int




def parse_s3_url(s3_url: str) -> tuple[str, str]:
    parsed = urlparse(s3_url)
    return parsed.netloc, parsed.path.lstrip("/")


def encode_image_base64(
    image_path: str
):
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(path, "rb") as f:
        image_bytes = f.read()

    encoded_str = base64.b64encode(image_bytes).decode("utf-8")
    return encoded_str


class ImageEmbeddingTask(BaseTask[
    list[ImageArtifact], ImageEmbeddingArtifact, ImageEmbeddingSettings
]):
    def __init__(
        self,
        artifact_visitor: ArtifactPersistentVisitor,
        config: ImageEmbeddingSettings,
    ):
        super().__init__(
            name=ImageEmbeddingTask.__name__,
            visitor=artifact_visitor,
            config=config
        )
    
    
    

    async def preprocess(self, input_data: list[ImageArtifact]) -> list[ImageEmbeddingArtifact]:        
        result = []
        for img_artifact in input_data:
            image_embedding_artifact = ImageEmbeddingArtifact(
                frame_index=img_artifact.frame_index,
                related_video_id=img_artifact.related_video_id,
                user_bucket=img_artifact.user_bucket,
                image_minio_url=img_artifact.minio_url_path,
                segment_index=img_artifact.segment_index,
                extension=img_artifact.extension,
                image_id=img_artifact.artifact_id,
                artifact_type=ImageEmbeddingArtifact.__name__
            )
            result.append(image_embedding_artifact)
        return result
    

        

    async def execute(self, input_data:list[ImageEmbeddingArtifact], client: BaseServiceClient|None|BaseMilvusClient) -> AsyncIterator[tuple[ImageEmbeddingArtifact, BinaryIO|None]]:
        assert client is not None, "The execution required client service"
        assert isinstance(client, BaseServiceClient)
        batch: list[ImageEmbeddingArtifact] = []
        batches: list[list[ImageEmbeddingArtifact]] = []

        while input_data:
            artifact = input_data.pop(0)

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
            images_local_paths = await asyncio.gather(*[
                fetch_object_from_s3(artifact.image_minio_url, self.visitor.minio_client, suffix=artifact.extension)
                for artifact in batch
            ])
            batch_images_encode = [encode_image_base64(p) for p in images_local_paths]

            request = ImageEmbeddingRequest(
                image_base64=batch_images_encode,
                metadata={}
            )

            response = await client.make_request(
                method='POST',
                endpoint=client.inference_endpoint,
                request_data=request)
            
            parsed = ImageEmbeddingResponse.model_validate(response)
            embeddings = parsed.embeddings

            for artifact, embedding in zip(batch, embeddings):
                buffer = io.BytesIO(json.dumps(embedding).encode("utf-8"))
                yield artifact, buffer
        
    
    async def postprocess(self, output_data: tuple[ImageEmbeddingArtifact, BinaryIO|None]) -> ImageEmbeddingArtifact:
        artifact, data = output_data
        if data is None:
            return artifact

        await artifact.accept_upload(self.visitor, data)
        return artifact


