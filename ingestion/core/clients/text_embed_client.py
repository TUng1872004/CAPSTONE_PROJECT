from typing import Optional


from core.clients.base import BaseServiceClient, ClientConfig, ClientError
from prefect_agent.service_text_embedding.schema import TextEmbeddingRequest, TextEmbeddingResponse 


class TextEmbeddingClient(BaseServiceClient[TextEmbeddingRequest, TextEmbeddingResponse]):
    """
    Client for the LLM (Large Language Model) service.
    
    This client communicates with the LLM microservice to perform
    multimodal inference tasks with text and optional images.
    """
    
    @property
    def service_name(self) -> str:
        return "service-text-embedding"
    
    @property
    def inference_endpoint(self) -> str:
        return '/text-embedding/infer'

    @property
    def load_endpoint(self) -> str:
        return '/text-embedding/load'

    @property
    def unload_endpoint(self) -> str:
        return '/text-embedding/unload'

    @property
    def models_endpoint(self) -> str:
        return '/text-embedding/models'
    
    @property
    def status_endpoint(self) -> str:
        return  '/text-embedding/status'
