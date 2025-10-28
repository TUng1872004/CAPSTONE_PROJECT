from .base import BaseMilvusClient
from .schema import VisualImageMilvusResponse,VisualImageFilterCondition, CaptionImageMilvusResponse, CaptionImageFilterCondition, SegmentCaptionMilvusResponse, SegmentCaptionFilterCondition
from typing import cast
from pymilvus import AsyncMilvusClient,AnnSearchRequest,WeightedRanker


class VisualImageMilvusClient(BaseMilvusClient[VisualImageMilvusResponse]):
    def __init__(self, uri:str, collection_name:str, ann_field: str):
        super().__init__(
            uri=uri,
            collection=collection_name
        )
        self.ann_field = ann_field

    @staticmethod
    def _hit_to_item(hit) -> VisualImageMilvusResponse:
        fields = hit.fields if hasattr(hit, "fields") else hit.entity["fields"]
        try:
            return VisualImageMilvusResponse(
                    identification=str(fields["id"]),
                    related_video_id=str(fields["related_video_id"]),
                    minio_url=str(fields["minio_url"]),
                    user_bucket=str(fields["user_bucket"]),
                    timestamp=str(fields['timestamp']),
                    frame_index=int(fields['frame_index']),
                    score=float(hit.score),
                )
        except Exception as e:
            missing = e.args[0]
            raise KeyError(f"Missing expected field '{missing}' in Milvus hit: {fields}")
    

    async def search_dense(
        self,
        query_embedding: list[list[float]],
        top_k: int,
        metric_type: str,
        param:dict,
        output_fields: list[str], 
        filter_expr: VisualImageFilterCondition,
    ) ->list[VisualImageMilvusResponse]:
        
        client = cast(AsyncMilvusClient, self.client)
        search_params = {}
        search_params['metric_type'] = metric_type
        search_params['params']= param

        res = await client.search( 
            collection_name=self.collection,
            data=query_embedding,
            anns_field=self.ann_field,
            limit=top_k,
            output_fields=output_fields,
            filter=filter_expr.to_expr(),
            search_params=search_params
        )
        return self._from_hit_to_response(res)



    


class CaptionImageMilvusClient(BaseMilvusClient[CaptionImageMilvusResponse]):
    def __init__(self, uri:str, collection_name:str, ann_field: str):
        super().__init__(
            uri=uri,
            collection=collection_name
        )
        self.ann_field = ann_field
    
    @staticmethod
    def _hit_to_item(hit) -> CaptionImageMilvusResponse:
        fields = hit.fields if hasattr(hit, "fields") else hit.entity["fields"]
        try:
            return CaptionImageMilvusResponse(
                    identification=str(fields["id"]),
                    frame_index=int(fields['frame_index']),
                    timestamp=str(fields['timestamp']),
                    related_video_id=str(fields["related_video_id"]),
                    caption=str(fields['caption']),
                    caption_minio_url=str(fields['caption_minio_url']),
                    score=float(hit.score),
                    image_minio_url=str(fields['image_minio_url']),
                    user_bucket=str(fields['userr_bucket'])
                )
        except Exception as e:
            missing = e.args[0]
            raise KeyError(f"Missing expected field '{missing}' in Milvus hit: {fields}")
    
    async def search_dense(
        self,
        query_embedding: list[list[float]],
        top_k: int,
        metric_type: str,
        param:dict,
        output_fields: list[str], 
        filter_expr: CaptionImageFilterCondition,
    ) ->list[CaptionImageMilvusResponse]:
        
        client = cast(AsyncMilvusClient, self.client)
        search_params = {}
        search_params['metric_type'] = metric_type
        search_params['params']= param

        res = await client.search( 
            collection_name=self.collection,
            data=query_embedding,
            anns_field=self.ann_field,
            limit=top_k,
            output_fields=output_fields,
            filter=filter_expr.to_expr(),
            search_params=search_params
        )
        return self._from_hit_to_response(res)

    


class SegmentCaptionImageMilvusClient(BaseMilvusClient[SegmentCaptionMilvusResponse]):
    def __init__(self, uri:str, collection_name:str, ann_field: str):
        super().__init__(
            uri=uri,
            collection=collection_name
        )
        self.ann_field = ann_field
    
    @staticmethod
    def _hit_to_item(hit) -> SegmentCaptionMilvusResponse:
        fields = hit.fields if hasattr(hit, "fields") else hit.entity["fields"]
        try:
            return SegmentCaptionMilvusResponse(
                identification=str(fields['id']),
                start_frame=int(fields['start_frame']),
                end_frame=int(fields['end_frame']),
                start_time=str(fields['start_time']),
                end_time=str(fields['end_time']),
                related_video_id=str(fields['related_video_id']),
                caption=str(fields['caption']),
                segment_caption_minio_url=str(fields['segment_caption_minio_url']),
                user_bucket=str(fields['user_bucket']),
                score=float(hit.score)
            )
        except KeyError as e:
            raise KeyError(f"Missing expected field in Milvus hit: {e}") from e

    
    async def search_dense(
        self,
        query_embedding: list[list[float]],
        top_k: int,
        metric_type: str,
        param:dict,
        output_fields: list[str], 
        filter_expr: SegmentCaptionFilterCondition,
    ) ->list[SegmentCaptionMilvusResponse]:
        
        client = cast(AsyncMilvusClient, self.client)
        search_params = {}
        search_params['metric_type'] = metric_type
        search_params['params']= param

        res = await client.search( 
            collection_name=self.collection,
            data=query_embedding,
            anns_field=self.ann_field,
            limit=top_k,
            output_fields=output_fields,
            filter=filter_expr.to_expr(),
            search_params=search_params
        )
        return self._from_hit_to_response(res)