from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Union

import numpy as np
import open_clip
import torch #type:ignore
import base64
from io import BytesIO
from PIL import Image

from shared.registry import BaseModelHandler, register_model
from shared.schema import ModelInfo
from service_image_embedding.core.config import ImageEmbeddingConfig
from service_image_embedding.schema import ImageEmbeddingRequest, ImageEmbeddingResponse

ImageInput = Union[str, Path, Image.Image]


def _resolve_device(requested: Literal["cpu", "cuda"]) -> str:
    if requested == "cuda" and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _move_to_device(module: torch.nn.Module, device: str) -> torch.nn.Module:
    return module.to(torch.device(device))


@register_model("open_clip")
class OpenCLIPImageEmbedding(BaseModelHandler[ImageEmbeddingRequest, ImageEmbeddingResponse]):
    def __init__(self, model_name: str, config: ImageEmbeddingConfig):
        super().__init__(model_name, config)
        self._model_name = config.open_clip_model_name
        self._pretrained = config.open_clip_pretrained
        self.model: torch.nn.Module | None = None
        self.preprocess = None
        self.device: str | None = None

    async def load_model_impl(self, device: Literal["cpu", "cuda"]) -> None:
        if self.model is not None:
            return

        actual_device = _resolve_device(device)
        model, _, preprocess = open_clip.create_model_and_transforms(
            self._model_name,
            pretrained=self._pretrained,
        )
        model = _move_to_device(model, actual_device)
        model.eval()

        self.model = model
        self.preprocess = preprocess
        self.device = actual_device

    async def unload_model_impl(self) -> None:
        if self.model is not None:
            del self.model
        self.model = None
        self.preprocess = None
        self.device = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    async def preprocess_input(self, input_data: ImageEmbeddingRequest) -> torch.Tensor:
        if self.preprocess is None or self.device is None:
            raise RuntimeError("Model not loaded")

        tensors: List[torch.Tensor] = []
        for image_base64 in input_data.image_base64:
            image_bytes = base64.b64decode(image_base64)
            image_buf = BytesIO(image_bytes)
            img = Image.open(image_buf)

            tensor = self.preprocess(img) #type:ignore
            tensors.append(tensor)

        batch = torch.stack(tensors, dim=0).to(self.device)
        return batch

    async def run_inference(self, preprocessed_data: torch.Tensor) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        with torch.no_grad():
            features = self.model.encode_image(preprocessed_data)
            features = torch.nn.functional.normalize(features, dim=-1)
            embeddings = features.cpu().numpy().astype(np.float32)
        return embeddings

    async def postprocess_output(
        self,
        output_data: np.ndarray,
        original_input_data: ImageEmbeddingRequest,
    ) -> ImageEmbeddingResponse:
        return ImageEmbeddingResponse(
            embeddings=output_data.tolist(),
            metadata=original_input_data.metadata,
            status="success",
        )

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(
            model_name=f"{self._model_name}-{self._pretrained}",
            model_type="image_embedding",
        )

    def _load_image(self, image_input: ImageInput) -> Image.Image:
        if isinstance(image_input, (str, Path)):
            return Image.open(image_input).convert("RGB")
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        raise ValueError(f"Unsupported image type: {type(image_input)}")
