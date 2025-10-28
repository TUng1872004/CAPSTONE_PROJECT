from pydantic import BaseModel, Field




class VisualImageMilvusResponse(BaseModel):
    identification: str
    related_video_id: str
    frame_index: int
    timestamp: str
    minio_url: str
    user_bucket: str
    score: float

class VisualImageFilterCondition(BaseModel):
    related_video_id: list[str] | None = None
    user_bucket: str | None = None

    def to_expr(self) -> str:
        parts = []
        if self.related_video_id:
            ids = ', '.join(f'"{v}"' for v in self.related_video_id)
            parts.append(f"related_video_id in [{ids}]")
        if self.user_bucket:
            parts.append(f'user_bucket == "{self.user_bucket}"')
        return " and ".join(parts) if parts else ""



class CaptionImageMilvusResponse(BaseModel):
    identification: str
    frame_index:int
    timestamp: str
    related_video_id: str
    caption: str
    caption_minio_url: str
    user_bucket:str
    score:float

    image_minio_url:str

    




class CaptionImageFilterCondition(BaseModel):
    related_video_id: list[str] | None = None
    user_bucket: str | None = None

    def to_expr(self) -> str:
        parts = []
        if self.related_video_id:
            ids = ', '.join(f'"{v}"' for v in self.related_video_id)
            parts.append(f"related_video_id in [{ids}]")
        if self.user_bucket:
            parts.append(f'user_bucket == "{self.user_bucket}"')
        return " and ".join(parts) if parts else ""



class SegmentCaptionMilvusResponse(BaseModel):
    identification: str
    start_frame: int
    end_frame: int
    start_time: str
    end_time: str
    related_video_id: str
    caption:str
    segment_caption_minio_url: str
    user_bucket:str
    score: float




class SegmentCaptionFilterCondition(BaseModel):
    related_video_id: list[str] | None = None
    user_bucket: str | None = None

    def to_expr(self) -> str:
        parts = []
        if self.related_video_id:
            ids = ', '.join(f'"{v}"' for v in self.related_video_id)
            parts.append(f"related_video_id in [{ids}]")
        if self.user_bucket:
            parts.append(f'user_bucket == "{self.user_bucket}"')
        return " and ".join(parts) if parts else ""

