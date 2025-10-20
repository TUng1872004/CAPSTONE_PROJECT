from typing import Dict, Any, Optional

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from threading import Lock
import uuid
from core.artifact.schema import VideoArtifact, AutoshotArtifact, ASRArtifact, ImageArtifact, SegmentCaptionArtifact, ImageCaptionArtifact, ImageEmbeddingArtifact, TextCapSegmentEmbedArtifact


class ProcessingStage(str, Enum):
    VIDEO_INGEST = "video_ingest"              
    AUTOSHOT_SEGMENTATION = "autoshot_segmentation"  
    ASR_TRANSCRIPTION = "asr_transcription"     
    IMAGE_EXTRACTION = "image_extraction"       
    SEGMENT_CAPTIONING = "segment_captioning"  
    IMAGE_CAPTIONING = "image_captioning"       
    IMAGE_EMBEDDING = "image_embedding"         
    TEXT_CAP_SEGMENT_EMBEDDING = "text_cap_segment_embedding" 


@dataclass
class StageProgress:
    stage: ProcessingStage
    total_items: int = 0
    completed_items: int = 0
    percentage: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    details: dict[str, Any]|None = None

class RunStatus(str,Enum):
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'

@dataclass
class VideoProgress:
    run_id: str
    overall_percentage: float = 0.0
    current_stage: Optional[ProcessingStage] = None
    stages: Dict[ProcessingStage, StageProgress] | None = None
    start_time: datetime | None= None
    end_time: Optional[datetime] = None
    status: RunStatus = RunStatus.RUNNING  # running, completed, failed
    error: Optional[str] = None

class ProgressTracker:
    def __init__(self) -> None:
        self._progress: Dict[str, VideoProgress] = {}
        self._lock = Lock()
    
    def start_video(self, video_id: str, total_stages:int=len(ProcessingStage)) -> None:
        with self._lock:
            self._progress[video_id] = VideoProgress(
                run_id=video_id,
                stages={stage: StageProgress(stage=stage) for stage in ProcessingStage},
                start_time=datetime.now(),
                overall_percentage=0.0
            )
    
    def update_stage_progress(
        self, 
        video_id: str,
        stage: ProcessingStage,
        total_items: int,
        completed_items: int,
        details: dict[str, Any] | None=None
    ):
        with self._lock:
            if video_id not in self._progress:
                return  

            run_progress = self._progress[video_id]
            if not run_progress.stages or ( run_progress.stages and stage not in run_progress.stages):
                return

            stage_progress = run_progress.stages[stage]
            stage_progress.total_items = total_items
            stage_progress.completed_items = completed_items
            stage_progress.percentage = (completed_items / total_items * 100) if total_items > 0 else 0.0
            stage_progress.details = details or {}
            if stage_progress.start_time is None:
                stage_progress.start_time = datetime.now()
            
            completed_stages = sum(1 for s in run_progress.stages.values() if s.percentage >= 100)
            run_progress.overall_percentage = (completed_stages / len(ProcessingStage)) * 100
            run_progress.current_stage = stage
        
    def complete_stage(self, video_id: str, stage: ProcessingStage) -> None:
        with self._lock:
            if video_id in self._progress and stage in self._progress[video_id].stages: #type:ignore
                self._progress[video_id].stages[stage].end_time = datetime.now() #type:ignore
        
    def complete_run(self, video_id: str, status: RunStatus = RunStatus.COMPLETED, error: Optional[str] = None) -> None:
        with self._lock:
            if video_id in self._progress:
                self._progress[video_id].status = status
                self._progress[video_id].end_time = datetime.now()
                self._progress[video_id].error = error
                if status == "completed":
                    self._progress[video_id].overall_percentage = 100.0
    
    def get_progress(self, video_id: str) -> Optional[VideoProgress]:
        with self._lock:
            return self._progress.get(video_id)

    def remove_video_id(self, video_id: str) -> None:
        with self._lock:
            self._progress.pop(video_id, None)
    

    def clear_video_progress_cache(self):
        self._progress.clear()


            


