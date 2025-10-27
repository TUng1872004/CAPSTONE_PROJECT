from __future__ import annotations
import os
from functools import lru_cache
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioSettings(BaseSettings):
    """Configuration for interacting with the MinIO object store."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MINIO_", extra="ignore")
class PrefectSettings(BaseSettings):
    """Configuration for Prefect server communication."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="PREFECT_", extra="ignore")

    api_url: str = Field(default="http://prefect-server:4200/api", description="Prefect API URL reachable from clients")
    work_pool: str = Field(default="default-agent-pool", description="Prefect work pool name for worker submissions")
    work_queue: Optional[str] = Field(default=None, description="Optional Prefect work queue name")
    default_run_name: str = Field(default="video-processing-run", description="Fallback name for created flow runs")
    deployment_name: Optional[str] = Field(default=None, description="Fully qualified Prefect deployment name (flow/deployment)")


class UploadSettings(BaseSettings):
    """Upload validation and handling settings for the FastAPI surface."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="UPLOAD_", extra="ignore")

    max_size_mb: int = Field(default=512, description="Maximum size of a single uploaded file in megabytes")
    allow_multiple: bool = Field(default=True, description="Whether multi-file uploads are accepted")
    allowed_content_types: List[str] = Field(
        default_factory=lambda: ["video/mp4", "video/quicktime", "video/x-matroska"],
        description="List of allowed MIME types",
    )

    @field_validator("allowed_content_types", mode="before")
    @classmethod
    def split_allowed_types(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def max_size_bytes(self) -> int:
        return int(self.max_size_mb * 1024 * 1024)


class ServiceSettings(BaseSettings):
    """Endpoints and defaults for downstream GPU services."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SERVICE_", extra="ignore")

    autoshot_url: str = Field(default="http://localhost:8001", description="Base URL for the AutoShot segmentation service")
    asr_url: str = Field(default="http://localhost:8002", description="Base URL for the ASR batch service")
    request_timeout_seconds: int = Field(default=300, description="HTTP timeout for service calls")
    max_retries: int = Field(default=2, description="Number of retries for failed service calls")
    retry_backoff_seconds: float = Field(default=5.0, description="Backoff duration between retries")


class AppSettings(BaseModel):
    """Aggregate settings container exposed to the application."""

    environment: str = Field(default="local", description="Current runtime environment identifier")
    minio: MinioSettings
    prefect: PrefectSettings
    upload: UploadSettings
    services: ServiceSettings






@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return a cached instance of application settings."""

    environment = os.getenv("ENVIRONMENT", "local")
    return AppSettings(
        environment=environment,
        minio=MinioSettings(),
        prefect=PrefectSettings(),
        upload=UploadSettings(),
        services=ServiceSettings(),
    )


settings = get_settings()
"""Module-level cached settings for convenience."""

__all__ = [
    "AppSettings",
    "MinioSettings",
    "PrefectSettings",
    "ServiceSettings",
    "UploadSettings",
    "get_settings",
    "settings",
]
