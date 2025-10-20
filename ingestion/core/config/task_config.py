from typing import Literal, Any
from pydantic import Field
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

class VideoIngestionTaskConfig(BaseSettings):
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    user_bucket: str = "user-videos"
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="INGESTION",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )


class AutoshotTaskConfig(BaseSettings):
    model_name: str = "autoshot"
    device: Literal['cuda', 'cpu'] = 'cuda'
    user_bucket: str
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="AUTOSHOT",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

class ASRTaskConfig(BaseSettings):
    """Configuration for ASR processing task."""
    model_name: str = "chunkformer"
    device: Literal["cuda", "cpu"] = "cuda"
    user_bucket: str 
    

    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="ASR",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )


class ImageProcessingTaskConfig(BaseSettings):
    """Configuration for image extraction task."""
    num_img_per_segment: int = Field(default=3, ge=1)
    user_bucket: str 

    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="IMAGE",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

class LLMTaskConfig(BaseSettings):
    model_name: str = "gemini_api"
    device: Literal["cuda", "cpu"] = "cuda"
    image_per_segments: int = Field(default=5, ge=1)

    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="LLM",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )




class EmbeddingTaskConfig(BaseSettings):
    model_name: str = "open_clip"
    device: Literal["cuda", "cpu"] = "cuda"
    batch_size: int = Field(default=32, ge=1)

    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )



class MilvusTaskConfig(BaseSettings):
    """Configuration for Milvus persistence tasks."""
    host: str 
    port: str
    user: str 
    password: str 
    db_name: str 
    time_out: float = 30.0
    ingest_batch_size: int = Field(default=100, ge=1)

    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    cache_enabled: bool = False
    cache_expiration: timedelta | None = None
    persist_result: bool = False
    timeout_seconds: int | None = None
    limit_tag: str = Field(..., description="Concurrency tag name")
    occupy_slots: int = Field(default=1, ge=1, description="Number of slots to occupy")
    retries: int = Field(default=2, ge=0)
    retry_delay_seconds: int | list[int] = Field(default=10)

    model_config = SettingsConfigDict(
        env_prefix="INGESTION",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

PrefectConfig = VideoIngestionTaskConfig | AutoshotTaskConfig |ASRTaskConfig | ImageProcessingTaskConfig |LLMTaskConfig |EmbeddingTaskConfig |MilvusTaskConfig

def get_task_decorator_kwargs(config: PrefectConfig) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "name": config.name,
        "description": config.description,
        "tags": config.tags,
        "retries": config.retries,
        "retry_delay_seconds": config.retry_delay_seconds,
        "persist_result": config.persist_result,
    }
    
    if config.timeout_seconds:
        kwargs["timeout_seconds"] = config.timeout_seconds
    
    if config.cache_enabled and config.cache_expiration:
        from prefect.cache_policies import INPUTS, TASK_SOURCE
        kwargs["cache_policy"] = INPUTS + TASK_SOURCE
        kwargs["cache_expiration"] = config.cache_expiration
    
    return kwargs