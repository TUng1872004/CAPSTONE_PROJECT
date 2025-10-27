from typing import Any

from pydantic import BaseModel, Field


class TextEmbeddingRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, description="Collection of texts to embed")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TextEmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
    texts: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"
