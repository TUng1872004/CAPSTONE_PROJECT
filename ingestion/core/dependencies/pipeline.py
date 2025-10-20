from functools import lru_cache
from fastapi import Request

# === Task imports ===
from task.video_proc.main import VideoIngestionTask
from task.asr_task.main import ASRProcessingTask
from task.autoshot_task.main import AutoshotProcessingTask
from task.image_processing.main import ImageProcessingTask
from task.llm_segment_caption.main import SegmentCaptionLLMTask
from task.llm_image_caption.main import ImageCaptionLLMTask
from task.text_embedding.main import TextImageCaptionEmbeddingTask, TextCaptionSegmentEmbeddingTask
from task.image_embedding.main import ImageEmbeddingTask
from task.milvus_persist_task.main import ImageEmbeddingMilvusTask, TextImageCaptionMilvusTask, TextSegmentCaptionMilvusTask, MilvusCollectionConfig

# === Core ===
from core.clients.base import ClientConfig




@lru_cache(maxsize=1)
def get_client_config(request: Request) -> ClientConfig:
    return request.app.state.base_client_config

# ---------------------------------------------------------------------
# 🟩 Video Ingestion
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_video_ingestion_task(request: Request) -> VideoIngestionTask:
    return request.app.state.video_ingestion_task


# ---------------------------------------------------------------------
# 🟦 ASR
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_asr_task(request: Request) -> ASRProcessingTask:
    return request.app.state.asr_task



# ---------------------------------------------------------------------
# 🟨 Autoshot
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_autoshot_task(request: Request) -> AutoshotProcessingTask:
    return request.app.state.autoshot_task




# ---------------------------------------------------------------------
# 🟧 Image Processing
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_image_processing_task(request: Request) -> ImageProcessingTask:
    return request.app.state.image_processing_task


# ---------------------------------------------------------------------
# 🟪 LLM Segment Caption
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_segment_caption_llm_task(request: Request) -> SegmentCaptionLLMTask:
    return request.app.state.segment_caption_llm_task




# ---------------------------------------------------------------------
# 🟫 LLM Image Caption
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_image_caption_llm_task(request: Request) -> ImageCaptionLLMTask:
    return request.app.state.image_caption_llm_task




# ---------------------------------------------------------------------
# ⚪ Image Embedding
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_image_embedding_task(request: Request) -> ImageEmbeddingTask:
    return request.app.state.image_embedding_task




# ---------------------------------------------------------------------
# 🟢 Text & Caption Embedding
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_text_image_caption_embedding_task(request: Request) -> TextImageCaptionEmbeddingTask:
    return request.app.state.text_image_caption_embedding_task




@lru_cache(maxsize=1)
def get_text_caption_segment_embedding_task(request: Request) -> TextCaptionSegmentEmbeddingTask:
    return request.app.state.text_caption_segment_embedding_task




# ---------------------------------------------------------------------
# 🔵 Milvus Persistence Tasks
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_image_embedding_milvus_task(request: Request) -> ImageEmbeddingMilvusTask:
    return request.app.state.image_embedding_milvus_task

@lru_cache(maxsize=1)
def get_image_embedding_milvus_config(request: Request) -> MilvusCollectionConfig:
    return request.app.state.image_embedding_milvus_config


@lru_cache(maxsize=1)
def get_text_image_caption_milvus_task(request: Request) -> TextImageCaptionMilvusTask:
    return request.app.state.text_image_caption_milvus_task

@lru_cache(maxsize=1)
def get_text_image_caption_milvus_config(request: Request) -> MilvusCollectionConfig:
    return request.app.state.text_image_caption_milvus_config


@lru_cache(maxsize=1)
def get_text_segment_caption_milvus_task(request: Request) -> TextSegmentCaptionMilvusTask:
    return request.app.state.text_segment_caption_milvus_task

@lru_cache(maxsize=1)
def get_text_segment_caption_milvus_config(request: Request) -> MilvusCollectionConfig:
    return request.app.state.text_segment_caption_milvus_config