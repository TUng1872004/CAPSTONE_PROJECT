from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class ImageEmbeddingRequest(BaseModel):
    image_base64: list[str] | None= Field(None,min_length=1, description="Absolute paths to the input images")
    text_input: list[str] | None = Field(None,min_length=1, description="The list of texts that needs to be embed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata to echo back")

    @model_validator(mode='after')
    def validate_inputs(self) -> "ImageEmbeddingRequest":
        if not self.image_base64 and not self.text_input:
            raise ValueError("Either 'image_base64' or 'text_input' must be provided.")
        return self    


class ImageEmbeddingResponse(BaseModel):
    image_embeddings: list[list[float]] | None
    text_embeddings: list[list[float]] | None
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"
