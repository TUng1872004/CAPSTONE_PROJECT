from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Literal

from loguru import logger
from PIL import Image

from service_llm.core.config import LLMServiceConfig
from service_llm.schema import LLMRequest, LLMResponse
from shared.registry import BaseModelHandler, register_model
from shared.schema import ModelInfo
import base64
import io

def _load_image_from_b64(b64_str: str) -> Image.Image:
    """Decode a base64 image string into a PIL image."""
    if "," in b64_str:
        b64_str = b64_str.split(",", 1)[1]

    img_data = base64.b64decode(b64_str)
    img = Image.open(io.BytesIO(img_data))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img

@register_model("gemini_api")
class GeminiAPIHandler(BaseModelHandler[LLMRequest, LLMResponse]):

    def __init__(self, model_name: str, config: LLMServiceConfig) -> None:
        super().__init__(model_name, config)
        if not config.gemini_api_key:
            raise ValueError("Gemini API handler requires GEMINI_API_KEY to be set")
        self._api_key = config.gemini_api_key
        self._model_name = config.gemini_model_name
        self._client = None

    async def load_model_impl(self, device: Literal["cpu", "cuda"]) -> None:  
        if self._client is not None:
            return
        try:
            import google.generativeai as genai
        except ImportError as exc: 
            raise RuntimeError(
                "google-generativeai package is required for Gemini handler"
            ) from exc

        genai.configure(api_key=self._api_key) # type: ignore[attr-defined]
        self._client = genai.GenerativeModel(self._model_name) # type: ignore[attr-defined]
        logger.info("gemini_client_initialized", model=self._model_name)

    async def unload_model_impl(self) -> None:
        self._client = None

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(model_name=self._model_name, model_type="gemini_api")

    async def preprocess_input(self, input_data: LLMRequest) -> Dict[str, Any]:
        return {
            "prompt": input_data.prompt,
            "image_b64": input_data.image_base64,
            "metadata": input_data.metadata,
        }

    async def run_inference(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        if self._client is None:
            raise RuntimeError("Gemini client not initialized")

        prompt = preprocessed_data["prompt"]
        image_b64 = preprocessed_data["image_b64"]

        def _call_api() -> Dict[str, Any]:
            images = [_load_image_from_b64(path) for path in image_b64]
            parts: list[Any] = []
            parts.extend(images)
            parts.append(prompt)
            response = self._client.generate_content(parts)  # type: ignore[union-attr]
            answer_text = response.text if response and getattr(response, "text", None) else ""

            usage_metadata = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage_metadata, "prompt_token_count", None) if usage_metadata else None
            completion_tokens = (
                getattr(usage_metadata, "candidates_token_count", None) if usage_metadata else None
            )
            print(
                {
                    "answer": answer_text,
                    "input_tokens": prompt_tokens,
                    "output_tokens": completion_tokens,
                }

            )
            return {
                "answer": answer_text,
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
            }

        inference_result = await asyncio.to_thread(_call_api)
        return inference_result

    async def postprocess_output(
        self,
        output_data: Dict[str, Any],
        original_input_data: LLMRequest,
    ) -> LLMResponse:
        return LLMResponse(
            answer=output_data.get("answer", ""),
            metadata=original_input_data.metadata,
            model_name=self._model_name,
            status="success",
            input_tokens=output_data.get("input_tokens"),
            output_tokens=output_data.get("output_tokens"),
        )
