from pydantic import BaseModel, Field
from pathlib import Path
from typing import Any, Optional


class AutoShotRequest(BaseModel):
    s3_minio_url: str = Field(..., description="S3 Video path begin with s3://")
    metadata: dict | None = Field(None)

class AutoShotResponse(BaseModel):
    metadata: dict | None = Field(None)
    scenes: list[tuple[int,int]] = Field(..., description="List of (start_frame, end_frame) pairs")
    total_scenes: int
    status: str = 'success'

