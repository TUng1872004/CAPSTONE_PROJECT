from service_llm.model.gemini import GeminiAPIHandler  # noqa: F401
# from service_llm.model.moondream2 import Moondream2LocalHandler  # noqa: F401
from service_llm.model.openrouter import OpenRouterAPIHandler  # noqa: F401

AVAILABLE_LLM_MODELS = [
    "gemini_api",
    "openrouter_api",
]

__all__ = [
    "AVAILABLE_LLM_MODELS",
    "GeminiAPIHandler",
    "OpenRouterAPIHandler",
]
