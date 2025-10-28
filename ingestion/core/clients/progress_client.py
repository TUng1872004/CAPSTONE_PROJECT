import httpx
import asyncio
from pydantic import BaseModel, Field
from enum import Enum
from core.artifact.schema import VideoArtifact, AutoshotArtifact, ASRArtifact, ImageArtifact, SegmentCaptionArtifact, ImageCaptionArtifact, ImageEmbeddingArtifact, TextCapSegmentEmbedArtifact
from datetime import datetime
from threading import Lock

class ProcessingStage(str, Enum):
    VIDEO_INGEST = "video_ingest"              
    AUTOSHOT_SEGMENTATION = "autoshot_segmentation"  
    ASR_TRANSCRIPTION = "asr_transcription"     
    IMAGE_EXTRACTION = "image_extraction"       
    SEGMENT_CAPTIONING = "segment_captioning"  
    IMAGE_CAPTIONING = "image_captioning"       
    IMAGE_EMBEDDING = "image_embedding"         
    TEXT_CAP_SEGMENT_EMBEDDING = "text_cap_segment_embedding" 
    TEXT_CAP_IMAGE_EMBEDDING = "text_cap_image_embedding"

    IMAGE_MILVUS = "image_milvus"
    TEXT_CAP_SEGMENT_MILVUS = 'text_cap_segment_milvus'
    TEXT_CAP_IMAGE_MILVUS = 'text_cap_image_milvus'



class VideoProgress(BaseModel):
    video_id: str
    status: float = Field(..., description="The overall percentage", le=100.0, ge=0.0)
    complete_stages: list[ProcessingStage]  = Field(default=[ProcessingStage.VIDEO_INGEST])
    start_time: datetime | None= None
    end_time: datetime | None = None
    errors: str | None = None


class ProgressClient:
    def __init__(
        self,
        base_url: str,
        endpoint: str = '/api/ingestion/service/status/{video_id}'
    ):
        self.base_url = base_url
        self.endpoint = endpoint
        self._progress: dict[str, VideoProgress] = {}
        self._lock = Lock()
    
    async def start_video(
        self, video_id: str,
    ) -> dict:
        with self._lock:
            # remove old video id
            if video_id in self._progress:
                del self._progress[video_id]
            
            self._progress[video_id] = VideoProgress(
                video_id=video_id,
                start_time=datetime.now(),
                end_time=None,
                status=0.0,
                errors=None
            )

            async with httpx.AsyncClient(base_url=self.base_url) as client:
                response = await client.post(
                    self.endpoint.format(video_id=video_id),
                    json=self._progress[video_id].model_dump(mode='json')
                )
                response.raise_for_status()

            return response.json()

    def update_state_progress(
        self,
        video_id: str,
        stage: ProcessingStage,
    ):
        with self._lock:
            if video_id not in self._progress:
                return

            run_progress = self._progress[video_id]
            if stage in run_progress.complete_stages:
                
                return
            run_progress.complete_stages.append(stage)
            total_percentage = len(
                run_progress.complete_stages
            ) / len(ProcessingStage) * 100
            run_progress.status = total_percentage

    
    async def stream_progress(self, video_id: str) -> dict | None:
        with self._lock:
            progress_video = self._progress.get(video_id)
            if progress_video is None:
                return None
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                response = await client.post(
                    self.endpoint.format(video_id=video_id),
                    json=progress_video.model_dump(mode='json')
                ) 
                response.raise_for_status()
        
            return response.json()
    

    def clear_video_progress_cache(self):
        self._progress.clear()

            
