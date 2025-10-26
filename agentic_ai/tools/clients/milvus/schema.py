from pydantic import BaseModel, Field




class VisualImageMilvusResponse(BaseModel):
    identification: str
    related_video_name: str
    related_video_id: str
    segment_index: int
    minio_url: str
    user_bucket: str
    score: float

class VisualImageFilterCondition(BaseModel):
    related_video_id: str | None = None
    segment_index_min: int | None = None
    segment_index_max: int | None = None
    user_bucket: str | None = None

    def to_expr(self) -> str:
        parts = []
        if self.related_video_id:
            parts.append(f'related_video_id == "{self.related_video_id}"')
        if self.user_bucket:
            parts.append(f'user_bucket == "{self.user_bucket}"')
        if self.segment_index_min is not None:
            parts.append(f'segment_index >= {self.segment_index_min}')
        if self.segment_index_max is not None:
            parts.append(f'segment_index <= {self.segment_index_max}')
        return " and ".join(parts) if parts else ""


class CaptionImageMilvusResponse(BaseModel):
    identification: str
    frame_index:int
    related_video_name:str
    related_video_id: str
    caption: str
    caption_minio_url: str
    user_bucket:str


class CaptionImageFilterCondition(BaseModel):
    related_video_id: str | None = None
    
    def to_expr(self) -> str:
        raise NotImplemented



class SegmentCaptionMilvusResponse(BaseModel):
    """
    
    """

class SegmentCaptionFilterCondition(BaseModel):
    
    def to_expr(self) -> str:
        raise NotImplemented
     
    raise NotImplemented

