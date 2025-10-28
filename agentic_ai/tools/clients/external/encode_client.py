from ingestion.core.clients.image_embed_client import ImageEmbeddingClient
from ingestion.core.clients.text_embed_client import TextEmbeddingClient
from ingestion.prefect_agent.service_image_embedding.schema import ImageEmbeddingRequest, ImageEmbeddingResponse
from ingestion.prefect_agent.service_text_embedding.schema import TextEmbeddingRequest, TextEmbeddingResponse

from ingestion.task.image_embedding.main import ImageEmbeddingSettings
from ingestion.task.text_embedding.main import TextEmbeddingSettings

class ExternalEncodeClient:
    def __init__(
            self, 
            img_text_client: ImageEmbeddingClient,
            img_text_settings: ImageEmbeddingSettings, 
            txt_settings: TextEmbeddingSettings,
            txt_client: TextEmbeddingClient,    
        ):
        self.img_text_client = img_text_client
        self.img_text_settings = img_text_settings

        self.txt_client = txt_client
        self.txt_settings = txt_settings
        
    async def encode_visual_text(
        self,
        request: ImageEmbeddingRequest,
    )-> ImageEmbeddingResponse:
        
        await self.img_text_client.load_model(
            model_name=self.img_text_settings.model_name,
            device=self.img_text_settings.device
        )
        response = await self.img_text_client.make_request(
            method='POST',
            endpoint=self.img_text_client.inference_endpoint,
            request_data=request
        )  
        parsed = ImageEmbeddingResponse.model_validate(response)

        await self.img_text_client.unload_model()
        return parsed
    
    async def encode_text(
        self,
        request: TextEmbeddingRequest,
    )->TextEmbeddingResponse:
        await self.txt_client.load_model(
            model_name=self.txt_settings.model_name,
            device=self.txt_settings.device
        )
        response = await self.txt_client.make_request(
            method='POST',
            endpoint=self.txt_client.inference_endpoint,
            request_data=request
        )  
        parsed = TextEmbeddingResponse.model_validate(response)

        await self.txt_client.unload_model()
        return parsed

    