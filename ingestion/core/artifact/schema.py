from __future__ import annotations
from pydantic import BaseModel, Field
from typing import BinaryIO, Any, Literal
from datetime import datetime
import hashlib
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .persist import ArtifactPersistentVisitor


class BaseArtifact(ABC, BaseModel):
    
    @abstractmethod 
    def accept_upload(self, visitor: Any, upload_file: Any):
        raise NotImplementedError

    @abstractmethod
    def accept_check_exist(self, visitor: Any):
        raise NotImplementedError

    @property
    @abstractmethod
    def object_key(self)->str:
        raise NotImplementedError

    @property
    @abstractmethod
    def minio_url_path(self) -> str:
        raise NotImplementedError

    @property
    def artifact_id(self) -> str:
        raise NotImplementedError

class VideoArtifact(BaseArtifact):
    """
    This will hold the video artifact, This artifact is special, does not follow the BaseArtifact semantic conventional
    """
    artifact_type: str 
    task_name: str
    video_id: str
    video_minio_url: str
    video_extension: str
    user_bucket: str
    fps: float

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__

    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: dict):
        return visitor.visit_video(self, upload_file) 

    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor") -> bool:
        return await visitor._check_exist(self, self.user_bucket, check_minio=False)

    @property
    def object_key(self):
        raise NotImplementedError("Video artifact does not have this property")
    
    @property
    def minio_url_path(self):
        raise NotImplementedError("Video artifact does not have this property")

    @property
    def artifact_id(self) -> str:
       return self.video_id

class AutoshotArtifact(BaseArtifact):
    """
    This will hold the artifact segments after the autoshot processing
    """
    artifact_type: str
    related_video_id: str = Field(..., description="Which video id does this autoshot artifact belong to")
    related_video_minio_url: str
    related_video_extension: str
    related_video_fps: float

    task_name: str
    user_bucket: str

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__


    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: list):
        return visitor.visit_segments(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor"):
        return await visitor._check_exist(self, self.user_bucket)
    
    @property
    def object_key(self) -> str:
        return f"autoshot/{self.related_video_id}.json"

    @property
    def artifact_id(self) -> str:
        base_string = f"{self.related_video_id}:{self.related_video_id}:{self.task_name}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()
    
    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

class ASRArtifact(BaseArtifact):
    artifact_type: str  
    related_video_id: str = Field(..., description="Which video id does this autoshot artifact belong to")
    related_video_minio_url: str
    related_video_extension: str
    related_video_fps: float


    task_name: str
    user_bucket: str

    
    def __post_init__(self):
        self.artifact_type = self.__class__.__name__

    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: dict):
        return visitor.visit_asr(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor"):
        return await visitor._check_exist(self, self.user_bucket)

    @property
    def object_key(self) -> str:
        return f"asr/{self.related_video_id}.json"

    @property
    def artifact_id(self) -> str:
        base_string = f"{self.related_video_id}:{self.related_video_id}:{self.task_name}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

class ImageArtifact(BaseArtifact):
    artifact_type:str
    frame_index: int
    extension: str
    related_video_id: str
    related_video_minio_url: str
    related_video_extension: str
    related_video_fps: float
    timestamp: str
    


    autoshot_artifact_id: str

    user_bucket: str
    metadata: dict
    content_type: str

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__
    

    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: BinaryIO):
        return visitor.visit_image(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor"):
        return await visitor._check_exist(self, self.user_bucket)

    @property
    def object_key(self) -> str:
        return f"images/{self.related_video_id}/{self.frame_index:08d}{self.extension}"

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

    @property
    def artifact_id(self) -> str:
        checksum = self.metadata.get("checksum_md5", "")
        base_string = f"{self.related_video_id}:{self.frame_index}:{self.content_type}:{checksum}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()

class SegmentCaptionArtifact(BaseArtifact):
    
    artifact_type: str
    autoshot_artifact_id: str
    
    related_video_extension: str
    related_video_id: str
    related_video_fps: float
    
    start_frame: int
    end_frame: int
    start_timestamp: str
    end_timestamp: str

    related_asr: str
    related_video_minio_url: str
    user_bucket: str

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__

    
    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: str):
        return visitor.visit_segment_caption(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor") -> bool:
        return await visitor._check_exist(self, self.user_bucket)

    
    @property
    def object_key(self) -> str:
        return f"caption/segment/{self.related_video_id}/{self.start_frame}_{self.end_frame}.json"

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

    @property
    def artifact_id(self) -> str:
        base_string = f"{self.related_video_id}:{self.start_frame}:{self.end_frame}:{self.related_asr}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()
    
class ImageCaptionArtifact(BaseArtifact):
    artifact_type: str
    
    frame_index: int
    time_stamp: str
    related_video_id: str
    related_video_fps: float
    extension: str
    user_bucket: str
    image_minio_url: str
    image_id: str


    def __post_init__(self):
        self.artifact_type = self.__class__.__name__

    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: str):
        return visitor.visit_image_caption(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor") -> bool:
        return await visitor._check_exist(self, self.user_bucket)
    

    @property
    def object_key(self) -> str:
        return f"caption/image/{self.related_video_id}/{self.frame_index:08d}.json"

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

    @property
    def artifact_id(self) -> str:
        base_string = f"{self.image_id}:{self.related_video_id}:{self.frame_index}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()
    
class ImageEmbeddingArtifact(BaseArtifact):
    artifact_type: str
    time_stamp: str
    frame_index: int
    related_video_id: str
    related_video_fps: float
    user_bucket: str
    image_minio_url: str

    extension: str
    image_id: str

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__

    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: BinaryIO):
        return visitor.visit_image_embedding(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor") -> bool:
        return await visitor._check_exist(self, self.user_bucket)
    

    @property
    def object_key(self) -> str:
        return f"embedding/image/{self.related_video_id}/{self.frame_index:08d}.npy"

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

    @property
    def artifact_id(self) -> str:
        base_string = f"{self.image_id}:{self.related_video_id}:{self.frame_index}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()

class TextCaptionEmbeddingArtifact(BaseArtifact):
    artifact_type: str
    time_stamp: str
    related_frame_fps:float
    frame_index: int
    related_video_id: str
    image_caption_minio_url: str
    user_bucket:str
    caption_id: str
    image_minio_url: str

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__


    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: BinaryIO):
        return visitor.visit_image_caption_embedding(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor") -> bool:
        return await visitor._check_exist(self, self.user_bucket)
    

    @property
    def object_key(self) -> str:
        return f"embedding/image_caption/{self.related_video_id}/{self.frame_index:08d}.npy"

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"
    
    @property
    def artifact_id(self) -> str:
        base_string = f"{self.caption_id}:{self.related_video_id}:{self.frame_index}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()
    
class TextCapSegmentEmbedArtifact(BaseArtifact):
    artifact_type: str
    
    related_video_fps: float
    related_video_id: str

    start_frame: int
    end_frame: int
    start_time:str
    end_time:str

    related_segment_caption_url: str
    user_bucket:str
    segment_cap_id: str

    def __post_init__(self):
        self.artifact_type = self.__class__.__name__
        
    def accept_upload(self, visitor: "ArtifactPersistentVisitor", upload_file: BinaryIO):
        return visitor.visit_segment_caption_embedding(self, upload_file)
    
    async def accept_check_exist(self, visitor: "ArtifactPersistentVisitor") -> bool:
        return await visitor._check_exist(self, self.user_bucket)
    

    @property
    def object_key(self) -> str:
        return f"embedding/caption_segment/{self.related_video_id}/{self.start_frame}_{self.end_frame}.npy"

    @property
    def minio_url_path(self)->str:
        return f"s3://{self.user_bucket}/{self.object_key}"

    @property
    def artifact_id(self) -> str:
        base_string = f"{self.segment_cap_id}:{self.related_video_id}:{self.start_frame}:{self.end_frame}:{self.user_bucket}"
        return hashlib.sha512(base_string.encode("utf-8")).hexdigest()