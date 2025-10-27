from typing import Optional


from core.clients.base import BaseServiceClient, ClientConfig, ClientError
from prefect_agent.service_image_embedding.schema import ImageEmbeddingRequest, ImageEmbeddingResponse



class ImageEmbeddingClient(BaseServiceClient[ImageEmbeddingRequest, ImageEmbeddingResponse]):
    """
    Client for the LLM (Large Language Model) service.
    
    This client communicates with the LLM microservice to perform
    multimodal inference tasks with text and optional images.
    """
    
    @property
    def service_name(self) -> str:
        return "service-image-embedding"
    
    @property
    def inference_endpoint(self) -> str:
        return '/image-embedding/infer'

    @property
    def load_endpoint(self) -> str:
        return '/image-embedding/load'

    @property
    def unload_endpoint(self) -> str:
        return '/image-embedding/unload'

    @property
    def models_endpoint(self) -> str:
        return '/image-embedding/models'

    @property
    def status_endpoint(self) -> str:
        return  '/image-embedding/status'
