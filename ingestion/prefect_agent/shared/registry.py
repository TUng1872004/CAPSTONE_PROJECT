"""Model registry utilities shared across microservices."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Literal, Type, TypeVar

from pydantic import BaseModel

from shared.config import ServiceConfig
from shared.schema import ModelInfo

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseModelHandler(Generic[InputT, OutputT], ABC):
    """Interface each concrete model handler must implement."""

    def __init__(self, model_name: str, config: ServiceConfig) -> None:
        self.model_name = model_name
        self.config = config

    @abstractmethod
    async def load_model_impl(self, device: Literal["cpu", "cuda"]) -> None:
        """Load model weights into memory."""

    @abstractmethod
    async def unload_model_impl(self) -> None:
        """Release model resources."""

    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """Expose metadata for the loaded model."""

    @abstractmethod
    async def preprocess_input(self, input_data: InputT) -> Any:
        """Transform incoming request payload into model-ready tensors."""

    @abstractmethod
    async def run_inference(self, preprocessed_data: Any) -> Any:
        """Perform forward pass and return raw outputs."""

    @abstractmethod
    async def postprocess_output(self, output_data: Any, original_input_data: InputT) -> OutputT:
        """Convert raw outputs into the service response schema."""


MODEL_REGISTRY: Dict[str, Type[BaseModelHandler[Any, Any]]] = {}


def register_model(name: str):
    """Decorator used by model handlers to self-register."""

    def decorator(cls: Type[BaseModelHandler[Any, Any]]) -> Type[BaseModelHandler[Any, Any]]:
        MODEL_REGISTRY[name] = cls
        return cls

    return decorator


def list_models() -> list[str]:
    return sorted(MODEL_REGISTRY.keys())


def get_model_handler(name: str, config: ServiceConfig) -> BaseModelHandler[Any, Any]:
    if name not in MODEL_REGISTRY:
        available = ", ".join(list_models()) or "<none>"
        raise ValueError(f"Model {name} not registered. Available: {available}")
    return MODEL_REGISTRY[name](name, config)


__all__ = [
    "BaseModelHandler",
    "InputT",
    "MODEL_REGISTRY",
    "OutputT",
    "get_model_handler",
    "list_models",
    "register_model",
]
