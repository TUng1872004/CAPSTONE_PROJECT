from typing import Optional

from core.clients.base import BaseServiceClient, ClientConfig, ClientError
from prefect_agent.service_asr.core.schema import ASRInferenceRequest, ASRInferenceResponse


class ASRClientError(ClientError):
    pass

class ASRClient(BaseServiceClient[ASRInferenceRequest, ASRInferenceResponse]):
    @property
    def service_name(self) -> str:
        return "service-asr"
    
    @property
    def inference_endpoint(self) -> str:
        return '/asr/infer'

    @property
    def load_endpoint(self) -> str:
        return '/asr/load'

    @property
    def unload_endpoint(self) -> str:
        return '/asr/unload'

    @property
    def models_endpoint(self) -> str:
        return '/asr/models'


    @property
    def status_endpoint(self) -> str:
        return '/asr/status'
    

    
    

    