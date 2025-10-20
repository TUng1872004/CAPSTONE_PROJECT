from typing import Union, Literal
import torch #type:ignore
import numpy as np
from PIL import Image
from transformers import XLMRobertaTokenizer
from timm import create_model
from .beit3_components import modeling_finetune
from .procesor import Processor
from shared.registry import BaseModelHandler, register_model
from shared.schema import ModelInfo
from service_image_embedding.schema import ImageEmbeddingRequest, ImageEmbeddingResponse
from service_image_embedding.core.config import ImageEmbeddingConfig

import base64
from io import BytesIO
from PIL import Image


def move_to_device(model, device: str):
    if device == "cuda" and torch.cuda.is_available():
        return model.to("cuda")
    else:
        return model.to("cpu")

# @register_model('beit3')
class BEiT3ImageEmbedding(BaseModelHandler[ImageEmbeddingRequest, ImageEmbeddingResponse]):
    def __init__(self, model_name, config: ImageEmbeddingConfig):
        super().__init__(model_name, config)
        self.model_checkpoint = config.beit3_model_checkpoint
        self.tokenizer_checkpoint = config.beit3_tokenizer_checkpoint
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.device = None
    
    async def load_model_impl(self, device: Literal["cpu", "cuda"]):
        if self.model is not None:
            return
        self._tokenizer = XLMRobertaTokenizer(self.tokenizer_checkpoint)
        self._processor = Processor(
            self._tokenizer
        )
        self.model = create_model('beit3_large_patch16_384_retrieval', pretrained=False)
        checkpoint = torch.load(self.model_checkpoint, map_location="cpu")
        self.model.load_state_dict(checkpoint['model'], strict=True)
        self.model = move_to_device(self.model, device)
        self.device=device
        self.model.eval()

    async def unload_model_impl(self):
        del self.model
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.device=None
    
    async def preprocess_input(self, input_data: ImageEmbeddingRequest) -> torch.Tensor:
        batch_tensor = []
        for imagebase64 in input_data.image_base64:
            image_bytes = base64.b64decode(imagebase64)
            image_buf = BytesIO(image_bytes)
            img = Image.open(image_buf)
            tensor = self.processor(img) #type: ignore
            batch_tensor.append(tensor)
        batch_tensor = torch.vstack(batch_tensor).to(self.device)
        return batch_tensor
    
    async def run_inference(self, preprocessed_data: torch.Tensor) -> np.ndarray:
        with torch.no_grad():
            features, _ = self._model(image=preprocessed_data, only_infer=True) #type: ignore
            features = features / features.norm(dim=-1, keepdim=True)
            batch_features = features.cpu().numpy().astype(np.float32)
        return np.vstack(batch_features)
    
    async def postprocess_output(self, output_data: np.ndarray, original_input_data: ImageEmbeddingRequest):    
        embedding_list_arr = output_data.tolist()
        return ImageEmbeddingResponse(
            embeddings=embedding_list_arr,
            metadata=original_input_data.metadata,
            status='Successs'
        )
    
    def get_model_info(self) -> ModelInfo:
        return ModelInfo(
            model_name=self.model_checkpoint ,
            model_type='beit3'
        )



    def _load_image(self, image_input: Union[str, np.ndarray, Image.Image]) -> Image.Image:
        if isinstance(image_input, str):
            return Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            return Image.fromarray(image_input.astype("uint8"), "RGB")
        elif isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")

        

