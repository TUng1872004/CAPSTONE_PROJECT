"""Shared pydantic models used across the orchestration stack."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadMetadata(BaseModel):
    title: Optional[str] = Field(default=None, description="Optional human readable title")
    tags: List[str] = Field(default_factory=list, description="Optional tags associated with the upload")
    user_id: Optional[str] = Field(default=None, description="Identifier of the user initiating the upload")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for downstream consumers")


class VideoObject(BaseModel):
    object_key: str = Field(..., description="Object key within MinIO")
    filename: str = Field(..., description="Original filename provided by the client")
    file_size: int = Field(..., ge=0, description="Size of the file in bytes")
    content_type: str = Field(..., description="MIME type detected for the file")


class AutoShotResult(BaseModel):
    scenes_key: str = Field(..., description="Object key for stored AutoShot scene data")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Optional summary statistics")


class ASRResult(BaseModel):
    transcript_key: str = Field(..., description="Object key for stored ASR output")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Optional summary statistics")


class RunContext(BaseModel):
    run_id: str
    upload_metadata: UploadMetadata = Field(default_factory=UploadMetadata)
    video_objects: List[VideoObject]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunManifest(BaseModel):
    run_id: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    inputs: List[VideoObject] = Field(default_factory=list)
    autoshot: Optional[AutoShotResult] = None
    asr: Optional[ASRResult] = None
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def mark_running(self) -> "RunManifest":
        return self.model_copy(update={"status": ProcessingStatus.RUNNING})

    def mark_success(
        self,
        *,
        autoshot: Optional[AutoShotResult] = None,
        asr: Optional[ASRResult] = None,
    ) -> "RunManifest":
        return self.model_copy(
            update={
                "status": ProcessingStatus.COMPLETED,
                "completed_at": datetime.now(timezone.utc),
                "autoshot": autoshot or self.autoshot,
                "asr": asr or self.asr,
            }
        )

    def mark_failure(self, errors: List[str]) -> "RunManifest":
        return self.model_copy(
            update={
                "status": ProcessingStatus.FAILED,
                "completed_at": datetime.now(timezone.utc),
                "errors": errors,
            }
        )


class ManifestEnvelope(BaseModel):
    run: RunManifest
    upload_metadata: UploadMetadata


__all__ = [
    "ProcessingStatus",
    "UploadMetadata",
    "VideoObject",
    "AutoShotResult",
    "ASRResult",
    "RunContext",
    "RunManifest",
    "ManifestEnvelope",
]
