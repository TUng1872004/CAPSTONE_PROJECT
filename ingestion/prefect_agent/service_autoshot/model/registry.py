"""Autoshot model registry integration."""

from __future__ import annotations

from typing import Literal, cast
import asyncio
from shared.registry import BaseModelHandler, register_model
from shared.schema import ModelInfo
from service_autoshot.core.config import AutoshotConfig
from service_autoshot.model.autoshot import AutoShot
from service_autoshot.schema import AutoShotRequest, AutoShotResponse
from shared.storage import StorageClient, MinioSettings
from shared.util import fetch_object_from_s3
from loguru import logger

@register_model("autoshot")
class AutoshotModelHandler(BaseModelHandler[AutoShotRequest, AutoShotResponse]):
    def __init__(self, model_name: str, config: AutoshotConfig) -> None:
        super().__init__(model_name, config)
        self._service_config = config
        self._model: AutoShot | None = None
        self._device: str | None = None
        self._lock = asyncio.Lock()
        minio_settings = MinioSettings()
        self._client = StorageClient(minio_settings)

    async def load_model_impl(self, device: Literal["cpu", "cuda"]) -> None:
        async with self._lock:
            if self._model is not None:
                return
            model_path = self._service_config.autoshot_model_path
            self._model = AutoShot(pretrained_path=model_path, device=device)
            self._device = device

            logger.info(f"Mode autoshot has been loaded into memory")

    async def unload_model_impl(self) -> None:
        async with self._lock:
            if self._model is not None:
                del self._model
            self._model = None
            self._device = None

            logger.info(f"Mode autoshot has been unloaded from  memory")

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(model_name=self.model_name, model_type="autoshot")

    async def preprocess_input(self, input_data: AutoShotRequest) -> str:
        print(input_data.s3_minio_url)
        video_path = await fetch_object_from_s3(
            input_data.s3_minio_url, storage=self._client, suffix='.mp4'
        )
        logger.info(f"Video s3 path: {video_path} has been prepared")
        return video_path

    async def run_inference(self, preprocessed_data: str) -> list[list[int]]:
        if self._model is None:
            raise RuntimeError("Autoshot model not loaded")
        try:
            
            return self._model.process_video(preprocessed_data)
        finally:
            try:
                import os
                if os.path.exists(preprocessed_data):
                    os.remove(preprocessed_data)
            except Exception:
                pass

    async def postprocess_output(
        self,
        output_data: list[list[int]],
        original_input_data: AutoShotRequest,
    ) -> AutoShotResponse:
        scenes: list[tuple[int,int]] = cast(list[tuple[int,int]], [tuple(s) for s in output_data])

        logger.info(f"Video has been processed with total scenes: {len(scenes)=}")
        return AutoShotResponse(
            metadata=original_input_data.metadata,
            scenes=scenes,
            total_scenes=len(scenes),
            status="success",
        )


__all__ = ["AutoshotModelHandler"]
