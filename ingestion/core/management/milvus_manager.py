from __future__ import annotations
from typing import Dict, List

from pydantic import BaseModel, Field
from loguru import logger

# Ensure concrete clients are imported so BaseMilvusClient registry gets populated
from core.clients import milvus_client as _milvus_clients  # noqa: F401

from core.app_state import AppState
from core.clients.base import BaseMilvusClient, MilvusCollectionConfig
from core.config.storage import milvus_settings
from core.clients.milvus_client import ImageEmbeddingMilvusClient, TextCaptionEmbeddingMilvusClient, SegmentCaptionEmbeddingMilvusClient

class MilvusDeletionOutcome(BaseModel):
    success: bool
    user_id: str
    related_video_id: str
    per_collection_deleted: Dict[str, int] = Field(default_factory=dict)
    total_deleted: int = 0
    errors: List[str] = Field(default_factory=list)


class MilvusManager:

    def __init__(
        self,
        image_client: ImageEmbeddingMilvusClient,
        text_cap_client: TextCaptionEmbeddingMilvusClient,
        text_seg_client: SegmentCaptionEmbeddingMilvusClient,
    ) -> None:
        self.image_client = image_client
        self.text_cap_client = text_cap_client
        self.text_seg_client =  text_seg_client
        self._state = AppState()

    async def delete_by_related_video_id(self, user_id: str, related_video_id: str) -> MilvusDeletionOutcome:
        errors: list[str] = []
        per_collection: dict[str, int] = {}
        total = 0

        clients: list[tuple[str, BaseMilvusClient ]] = [
              ("image_embedding", self.image_client),
              ("text_caption_embedding", self.text_cap_client),
              ("segment_caption_embedding", self.text_seg_client),
        ]

        for collection_name, client in clients:
            try:
                if not await client.has_user_collection():
                    per_collection[collection_name] = 0
                    continue

                filter_expr = (
                    f'user_id == "{user_id}" and '
                    f'related_video_id == "{related_video_id}"'
                )
                deleted = await client.delete_by_filter(filter_expr)
                per_collection[collection_name] = deleted
                total += deleted

            except Exception as e:
                err = f"{client.__name__}: {e}"
                logger.exception("milvus_dynamic_delete_error", error=str(e))
                errors.append(err)

        outcome = MilvusDeletionOutcome(
            success=len(errors) == 0,
            user_id=user_id,
            related_video_id=related_video_id,
            per_collection_deleted=per_collection,
            total_deleted=total,
            errors=errors,
        )

        logger.info(
            "milvus_dynamic_delete_done",
            total_deleted=outcome.total_deleted,
            per_collection=outcome.per_collection_deleted,
            errors=outcome.errors,
        )

        return outcome
