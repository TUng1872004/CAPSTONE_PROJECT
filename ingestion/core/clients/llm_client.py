from typing import Optional


from core.clients.base import BaseServiceClient, ClientConfig, ClientError
from prefect_agent.service_llm.schema import LLMRequest, LLMResponse

class LLMClientError(ClientError):
    pass


class LLMClient(BaseServiceClient[LLMRequest, LLMResponse]):
    """
    Client for the LLM (Large Language Model) service.
    
    This client communicates with the LLM microservice to perform
    multimodal inference tasks with text and optional images.
    """
    
    @property
    def service_name(self) -> str:
        return "service-llm"

    
    @property
    def inference_endpoint(self) -> str:
        return '/llm/infer'

    @property
    def load_endpoint(self) -> str:
        return '/llm/load'

    @property
    def unload_endpoint(self) -> str:
        return '/llm/unload'

    @property
    def models_endpoint(self) -> str:
        return '/llm/models'
    
    @property
    def status_endpoint(self) -> str:
        return  '/llm/status'
