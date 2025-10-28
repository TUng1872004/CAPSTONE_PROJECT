from pydantic import Field, BaseModel


class VideoObject(BaseModel):
    """
    This will be the interface of a video
    """
    video_id: str
    fps: float



class SegmentObjectInterface(BaseModel):
    """
    This will be the interface of a segment
    """
    related_video_id: str = Field(..., description="The related video id that the segment belong to")
    start_frame_index: int = Field(..., description="The start frame index")
    end_frame_index: int 
    start_time: str
    end_time: str
    caption_info: str = Field(..., description="The overall detailed caption of the segment")


    def expr(self)->str:
        """
        Method that allow this artifact to represent itself in string format
        """
        return (
            f"[Video: {self.related_video_id}] "
            f"Frames {self.start_frame_index}-{self.end_frame_index} "
            f"({self.start_time} → {self.end_time}) | "
            f"Caption: {self.caption_info}"
        )

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

    timestamp: str = Field(
        ...,
        description="The timestamp corresponding to this frame in the video."
    )

    caption_info: str = Field(
        ...,
        description="Textual description or auto-generated caption for this frame."
    )

    minio_path: str = Field(
        ...,
        description="The storage path (e.g., in MinIO or S3) where the image file is located."
    )

    def expr(self) -> str:
        return (
            f"[Video: {self.related_video_id}] "
            f"Frame {self.frame_index} ({self.timestamp}) | "
            f"Path: {self.minio_path} | "
            f"Caption: {self.caption_info}"
        )





