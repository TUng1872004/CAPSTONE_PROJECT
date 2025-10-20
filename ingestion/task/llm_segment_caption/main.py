from __future__  import annotations
from tqdm.asyncio import tqdm
from typing import AsyncIterator, cast
import json
from core.pipeline.base_task import BaseTask
from core.clients.base import BaseServiceClient, BaseMilvusClient
from pydantic import BaseModel
from core.artifact.persist import  ArtifactPersistentVisitor 
from core.artifact.schema import AutoshotArtifact, ASRArtifact, SegmentCaptionArtifact
from prefect_agent.service_llm.schema import LLMRequest, LLMResponse
from task.common.util import fetch_object_from_s3

from .util import extract_images, return_related_asr_with_shot
from .prompt import SEGMENT_CAPTION_PROMPT
from typing import Literal
from core.config.logging import run_logger


class LLMCaptionSettings(BaseModel):
    model_name: str
    device: Literal['cuda', 'cpu']
    image_per_segments: int


class ShotASRInput(BaseModel):
    list_asrs: list[ASRArtifact]
    lists_autoshots: list[AutoshotArtifact]





class SegmentCaptionLLMTask(BaseTask[
    ShotASRInput, SegmentCaptionArtifact,LLMCaptionSettings,
]):
    def __init__(
        self,
        artifact_visitor: ArtifactPersistentVisitor,
        config: LLMCaptionSettings,
    ):
        super().__init__(
            name=SegmentCaptionLLMTask.__name__,
            visitor=artifact_visitor,
            config=config
        )
    
    async def preprocess(self, input_data: ShotASRInput) -> list[SegmentCaptionArtifact]:
        list_asr, list_autoshot = input_data.list_asrs, input_data.lists_autoshots        
        assert len(list_asr) == len(list_autoshot), "Not equal error"
       

        result = []
        for asr, shot in zip(list_asr, list_autoshot):
            asr_dict_path = await fetch_object_from_s3(asr.minio_url_path, self.visitor.minio_client, suffix='.json')
            autoshot_dict_path = await fetch_object_from_s3(shot.minio_url_path, self.visitor.minio_client, suffix='.json')

            asr_dict = json.load(open(asr_dict_path, 'r', encoding='utf-8'))
            autoshot_dict = json.load(open(autoshot_dict_path, 'r', encoding='utf-8'))


            tokens = asr_dict['tokens']
            segments: list[tuple[int,int]] = autoshot_dict['segments']

            for start_frame, end_frame in segments: 
                related_asr = return_related_asr_with_shot(
                    asr_tokens=tokens, #type:ignore
                    start_frame=start_frame,
                    end_frame=end_frame
                )
                artifact = SegmentCaptionArtifact(
                    related_video_name=shot.related_video_name,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    related_asr=related_asr,
                    related_video_minio_url=shot.related_video_minio_url,
                    user_bucket=asr.user_bucket,
                    related_video_extension=shot.related_video_extension,
                    autoshot_artifact_id=shot.artifact_id,
                    artifact_type=SegmentCaptionArtifact.__name__,
                    related_video_id=shot.related_video_id
                )
                result.append(artifact)

        run_logger.info (f"{len(result)=}")
        return result

    async def execute(self, input_data: list[SegmentCaptionArtifact], client: BaseServiceClient | None| BaseMilvusClient) -> AsyncIterator[tuple[SegmentCaptionArtifact, str | None]]:

        assert client is not None, "The execution required client service"
        assert isinstance(client, BaseServiceClient)
        run_logger.info("Before execute")
        
        
        for artifact in tqdm(input_data, desc="Processing segments"):
            run_logger.info("Before execute")
            exist = await artifact.accept_check_exist(self.visitor) 
            run_logger.debug(f"Exists: {exist}")
            if exist:
                yield artifact , None
                continue


            prompt = SEGMENT_CAPTION_PROMPT.format(
                asr=artifact.related_asr
            )
            local_video_path = await fetch_object_from_s3(artifact.related_video_minio_url, self.visitor.minio_client, suffix=artifact.related_video_extension)

            image_encode = extract_images(local_video_path, artifact.start_frame, artifact.end_frame, self.config.image_per_segments)

            request = LLMRequest(
                prompt=prompt,
                image_base64=image_encode,
                metadata={}
            )

            response = await client.make_request(
                method='POST',
                endpoint=client.inference_endpoint,
                request_data=request
            )
            parsed = LLMResponse.model_validate(response)
            caption = parsed.answer
            run_logger.info(f"Response: {caption}")
            yield artifact, caption
    
    async def postprocess(self, output_data: tuple[SegmentCaptionArtifact, str | None]) -> SegmentCaptionArtifact:

        artifact, caption = output_data
        if caption is None:
            return artifact

        await artifact.accept_upload(self.visitor, caption)
        return artifact
    

    