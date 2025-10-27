from pydantic import Field, BaseModel


class VideoObject(BaseModel):
    """
    This will be the interface of a video
    """
    video_id: str
    fps: float



class SegmentObject(BaseModel):
    """
    This will be the interface of a segment
    """
    related_video_id: str = Field(..., description="The related video id that the segment belong to")
    start_frame_index: int = Field(..., description="The start frame index")
    end_frame_index: int 
    start_time: float
    end_time: float
    caption_info: str = Field(..., description="The overall detailed caption of the segment")




class ImageObjectInterface(BaseModel):
    """
    This will be the interface of the image object
    """
    related_video_id: str = Field(
        ...,
        description="The unique identifier of the video this image/frame belongs to."
    )

    frame_index: int = Field(
        ...,
        description="The frame index within the video where this image was extracted."
    )

    timestamp: float = Field(
        ...,
        description="The timestamp (in seconds) corresponding to this frame in the video."
    )

    caption_info: str = Field(
        ...,
        description="Textual description or auto-generated caption for this frame."
    )

    minio_path: str = Field(
        ...,
        description="The storage path (e.g., in MinIO or S3) where the image file is located."
    )






