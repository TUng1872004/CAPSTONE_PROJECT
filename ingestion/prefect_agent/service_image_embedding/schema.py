from typing import Any

from pydantic import BaseModel, Field


class ImageEmbeddingRequest(BaseModel):
    image_base64: list[str] = Field(..., min_length=1, description="Absolute paths to the input images")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata to echo back")


class ImageEmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"
