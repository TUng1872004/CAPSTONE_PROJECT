from __future__ import annotations
from typing import AsyncIterator, Literal, cast  
from prefect import task
from pydantic import BaseModel
from core.pipeline.base_task import BaseTask
from core.artifact.persist import ArtifactPersistentVisitor
from core.artifact.schema import ASRArtifact, VideoArtifact
from prefect_agent.service_asr.core.schema import ASRInferenceRequest, ASRInferenceResponse
from core.clients.base import BaseMilvusClient, BaseServiceClient
from core.management.progress import ProcessingStage
from core.lifespan import AppState


tracker = AppState().progress_tracker



class ASRSettings(BaseModel):
    model_name: str
    device: Literal['cuda', 'cpu']



class ASRProcessingTask(BaseTask[list[VideoArtifact], ASRArtifact, ASRSettings]):
    def __init__(
        self, 
        artifact_visitor: ArtifactPersistentVisitor,
        config: ASRSettings,
    ):
        super().__init__(
            name=ASRProcessingTask.__name__,
            visitor=artifact_visitor,
            config=config
        )
        # Correct task name for ASR artifacts
        self.name = 'asr'

    async def preprocess(self, input_data: list[VideoArtifact]) -> list[ASRArtifact]:
        """
        Preprocess the video artifact
        1. Prepare the model
        """

        list_autoshot_artifact = []

        for video_art in input_data:
            autoshot_art = ASRArtifact(
                related_video_name=video_art.video_name,
                related_video_id=video_art.artifact_id,
                related_video_minio_url=video_art.minio_url_path,
                task_name=self.name,
                user_bucket=video_art.user_bucket,
                artifact_type=ASRArtifact.__name__
            )                
            list_autoshot_artifact.append(autoshot_art)
        return list_autoshot_artifact

    async def execute(self, input_data: list[ASRArtifact], client: BaseServiceClient| BaseMilvusClient | None) -> AsyncIterator[tuple[ASRArtifact, dict|None ]]:

        assert client is not None, "The execution required client service"
        assert isinstance(client, BaseServiceClient)

        
        for artifact in input_data:
            exist = await artifact.accept_check_exist(self.visitor)
            

            if exist:
                yield artifact, None
                continue
            
            request = ASRInferenceRequest(
                video_minio_url=artifact.related_video_minio_url,
                metadata={}
            )


            response = await client.make_request(
                method='POST',
                endpoint=client.inference_endpoint,
                request_data=request,
            )
            parsed = ASRInferenceResponse.model_validate(response)
            result_asr = parsed.result.model_dump(mode='json')
            yield artifact, result_asr
    
    async def postprocess(self, output_data: tuple[ASRArtifact, dict|None ]) -> ASRArtifact:        
        artifact, data = output_data
        if data is None:
            return artifact
        
        await artifact.accept_upload(self.visitor, data)
        return artifact

    
    

