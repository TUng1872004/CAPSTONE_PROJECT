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
                    related_video_name=str(fields["related_video_name"]),
                    related_video_id=str(fields["related_video_id"]),
                    segment_index=int(fields["segment_index"]),
                    minio_url=str(fields["minio_url"]),
                    user_bucket=str(fields["user_bucket"]),
                    score=float(hit.score),
                )
        except Exception as e:
            missing = e.args[0]
            raise KeyError(f"Missing expected field '{missing}' in Milvus hit: {fields}")
    

    async def search_dense(
        self,
        query_embedding: list[float],
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
            data=[query_embedding],
            anns_field=self.ann_field,
            limit=top_k,
            output_fields=output_fields,
            filter=filter_expr.to_expr(),
            search_params=search_params
        )
        return self._from_hit_to_response(res)



    


class CaptionImageMilvusClient(BaseMilvusClient[CaptionImageMilvusResponse]):
    def __init__(self, uri:str, collection_name:str, ann_field: str, sparse_field: str):
        super().__init__(
            uri=uri,
            collection=collection_name
        )
        self.ann_field = ann_field
        self.sparse_field = sparse_field
    
    @staticmethod
    def _hit_to_item(hit) -> CaptionImageMilvusResponse:
        raise NotImplemented
    
    def _construct_dense_request(
        self,
        *,
        data: list[float],
        top_k: int,
        param:dict,
        expr: CaptionImageFilterCondition
    ):
        return AnnSearchRequest(
            data=[data],
            anns_field=self.ann_field,
            param=param,
            limit=top_k,
            expr=expr.to_expr(),
        )

    def _construct_sparse_field(
        self,
        *,
        data: str,
        top_k: int,
        param:dict,
        expr: CaptionImageFilterCondition
    ):
        return AnnSearchRequest(
            data=[data],
            anns_field=self.ann_field,
            param=param,
            limit=top_k,
            expr=expr.to_expr(),
        )

    async def search_combination(
        self,
        requests: list[AnnSearchRequest],
        output_fields: list[str],   
        weights: tuple[float,float],
        limit: int,
    )->list[CaptionImageMilvusResponse]:
        assert len(requests) == len(weights), "Weights length must match requests"
        ranker = WeightedRanker(*weights)
        client = cast(AsyncMilvusClient, self.client)
        res = await client.hybrid_search(
            collection_name=self.collection,
            reqs=requests,
            output_fields=output_fields,            
            ranker=ranker,
            limit=limit
        )  
        return self._from_hit_to_response(res) 
    

class CaptionImageMilvusClient(BaseMilvusClient[SegmentCaptionMilvusResponse]):
    def __init__(self, uri:str, collection_name:str, ann_field: str, sparse_field: str):
        super().__init__(
            uri=uri,
            collection=collection_name
        )
        self.ann_field = ann_field
        self.sparse_field = sparse_field
    
    @staticmethod
    def _hit_to_item(hit) -> SegmentCaptionMilvusResponse:
        raise NotImplemented
    
    def _construct_dense_request(
        self,
        *,
        data: list[float],
        top_k: int,
        param:dict,
        expr: SegmentCaptionFilterCondition
    ):
        return AnnSearchRequest(
            data=[data],
            anns_field=self.ann_field,
            param=param,
            limit=top_k,
            expr=expr.to_expr(),
        )

    def _construct_sparse_field(
        self,
        *,
        data: str,
        top_k: int,
        param:dict,
        expr: SegmentCaptionFilterCondition
    ):
        return AnnSearchRequest(
            data=[data],
            anns_field=self.ann_field,
            param=param,
            limit=top_k,
            expr=expr.to_expr(),
        )

    async def search_combination(
        self,
        requests: list[AnnSearchRequest],
        output_fields: list[str],   
        weights: tuple[float,float],
        limit: int,
    )->list[SegmentCaptionMilvusResponse]:
        assert len(requests) == len(weights), "Weights length must match requests"
        ranker = WeightedRanker(*weights)
        client = cast(AsyncMilvusClient, self.client)
        res = await client.hybrid_search(
            collection_name=self.collection,
            reqs=requests,
            output_fields=output_fields,            
            ranker=ranker,
            limit=limit
        )  
        return self._from_hit_to_response(res) 