from typing import Any

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text provided to the model")
    image_base64: list[str] | None = Field(None, description="Optional list of image paths")
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    answer: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    model_name: str
    status: str = "success"
    input_tokens: int | None = Field(default=None, description="Number of input tokens consumed")
    output_tokens: int | None = Field(default=None, description="Number of output tokens generated")
