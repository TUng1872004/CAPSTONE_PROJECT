"""Import model handlers to ensure they are registered with the shared registry."""

# from service_image_embedding.model.beit3.beit3_embedding import BEiT3ImageEmbedding  # noqa: F401
from service_image_embedding.model.open_clip.openclip_embedding import OpenCLIPImageEmbedding  # noqa: F401

AVAILABLE_IMAGE_MODELS = [
    "open_clip",
    "beit3",
]

__all__ = [
    "AVAILABLE_IMAGE_MODELS",
    # "BEiT3ImageEmbedding",
    "OpenCLIPImageEmbedding",
]
