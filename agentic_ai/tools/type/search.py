from typing import Annotated, cast
from urllib.parse import urlparse
from collections import defaultdict
from agentic_ai.tools.schema.artifact import VideoObject, ImageObjectInterface, SegmentObjectInterface
from agentic_ai.tools.clients.milvus.client import VisualImageMilvusClient, VisualImageFilterCondition, CaptionImageFilterCondition, CaptionImageMilvusClient, SegmentCaptionFilterCondition, SegmentCaptionImageMilvusClient
from agentic_ai.tools.clients.external.encode_client import ExternalEncodeClient
from ingestion.prefect_agent.service_image_embedding.schema import ImageEmbeddingRequest
from ingestion.prefect_agent.service_text_embedding.schema import TextEmbeddingRequest
from agentic_ai.tools.clients.postgre.client import PostgresClient
from ingestion.core.artifact.schema import ImageCaptionArtifact
from agentic_ai.tools.clients.minio.client import StorageClient

def extract_s3_minio_url(s3_link:str) -> tuple[str,str]:
    parsed = urlparse(s3_link)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key

async def get_images_from_visual_query(
    query: Annotated[
        str,
        "A visually descriptive natural-language query (e.g., 'a red sports car on a wet street at night'). "
        "Avoid non-visual elements such as names, numbers, or abstract concepts."
    ],
    top_k: Annotated[int, "Number of top-matching images to retrieve based on similarity score."],
    
    list_video_id: Annotated[list[str], "List of video IDs to search within (auto-provided at runtime)."],
    user_id: Annotated[str, "User identifier for context or permissions (auto-provided)."],
    metric_type: Annotated[str, "Metric type for similarity computation (auto-provided)."],
    param: Annotated[dict, "Additional Milvus or embedding parameters (auto-provided)."],
    milvus_client: Annotated[VisualImageMilvusClient, "Milvus client for semantic retrieval (auto-provided)"],
    external_client: Annotated[ExternalEncodeClient, "External client (auto-provided)"],
    postgres_client: Annotated[PostgresClient, "Postgre client (auto-provided)"],
    minio_client: Annotated[StorageClient, "Storage Client (auto-provided)"],
    output_fields: list[str] = ['id', 'related_video_name', 'related_video_id', 'segment_index', 'minio_url', 'user_bucket']
) ->  list[tuple[float, ImageObjectInterface]]:
    """
    Retrieve visually similar images based on a **visual query**.
    This function performs a semantic search over a visual embedding index (e.g., Milvus)
    using a descriptive visual query, such as *"a sunset over mountains with orange clouds"*.

    (auto-provided): Ignore this parameters
    """

    embedding_request = ImageEmbeddingRequest(
        text_input=[query],
        image_base64=None,
        metadata={}
    )

    response = await external_client.encode_visual_text(request=embedding_request)
    query_embedding = cast(list[list[float]], response.image_embeddings) 
    
    filter_condition = VisualImageFilterCondition(
        related_video_id=list_video_id,
        user_bucket=user_id
    )

    milvus_response = await milvus_client.search_dense(
        query_embedding=query_embedding,
        top_k=top_k,
        metric_type=metric_type,
        param=param,
        output_fields=output_fields,
        filter_expr=filter_condition
    )

    result: list[tuple[float, ImageObjectInterface]] = []
    for resp in milvus_response:
        postgre_resp = await postgres_client.get_children_artifact(
            artifact_id=resp.identification,  filter_artifact_type=[ImageCaptionArtifact.__name__]
        )        
        caption_artifact = postgre_resp[0]
        s3_caption_url = caption_artifact.minio_url

        bucket_name, object_name = extract_s3_minio_url(s3_caption_url)
        caption_object = cast(dict, minio_client.read_json(
            bucket=bucket_name, object_name=object_name
        ))

        caption = caption_object['caption']

        image = ImageObjectInterface(
            related_video_id=resp.related_video_id,
            frame_index=resp.frame_index,
            timestamp=resp.timestamp,
            caption_info=caption,
            minio_path=resp.minio_url,
        )

        result.append((resp.score, image))
    

    return result



async def get_images_from_caption_query(
    caption_query: Annotated[
        str,
        "A descriptive text query that semantically aligns with image captions (e.g., 'a person surfing during sunset'). "
        "Use this for retrieving images based on caption embeddings rather than raw visual content."
    ],
    top_k: Annotated[int, "Number of top-matching images to retrieve based on caption embedding similarity."],
    list_video_id: Annotated[list[str], "List of video IDs to restrict the search domain (auto-provided)."],
    user_id: Annotated[str, "User identifier for context or permissions (auto-provided)."],
    metric_type: Annotated[str, "Metric type used for similarity computation in Milvus (auto-provided)."],
    param: Annotated[dict, "Additional Milvus or embedding parameters (auto-provided)."],
    milvus_client: Annotated[CaptionImageMilvusClient, "Milvus client for caption-based embedding search (auto-provided)."],
    external_client: Annotated[ExternalEncodeClient, "External encoding client for generating caption embeddings (auto-provided)."],
    postgres_client: Annotated[PostgresClient, "Postgres client for retrieving related artifact metadata (auto-provided)."],
    minio_client: Annotated[StorageClient, "Storage Client for reading caption data stored in MinIO (auto-provided)."],
    output_fields: list[str] = ['id', 'related_video_name', 'related_video_id', 'segment_index', 'minio_url', 'user_bucket']
) -> list[tuple[float, ImageObjectInterface]]:
    """
    Retrieve images semantically related to a **caption-based query**.

    This function performs a semantic search using **caption embeddings** instead of raw image embeddings.
    The query is encoded into the same embedding space as stored image captions,
    allowing text-to-image retrieval that aligns with descriptive annotations rather than pure visual features.
    """

    embedding_request = TextEmbeddingRequest(
        texts=[caption_query],
        metadata={}
    )
    response = await external_client.encode_text(request=embedding_request)
    query_embedding = cast(list[list[float]], response.embeddings)

    filter_condition =CaptionImageFilterCondition(related_video_id=list_video_id, user_bucket=user_id)

    milvus_response = await milvus_client.search_dense(
        query_embedding=query_embedding,
        top_k=top_k,
        metric_type=metric_type,
        param=param,
        output_fields=output_fields,
        filter_expr=filter_condition
    )
    result = []
    for resp in milvus_response:
        
        text_object = ImageObjectInterface(
            related_video_id=resp.related_video_id,
            frame_index=resp.frame_index,
            timestamp=resp.timestamp,
            caption_info=resp.caption,
            minio_path=resp.image_minio_url,
        )
        result.append((resp.score,text_object))
    return result



async def get_segments_from_event_query(
    event_query: Annotated[
        str,
        "An event-level natural language query (e.g., 'a person starts running', 'a car accident occurs', "
        "'a soccer player scores a goal'). This captures **temporal or semantic events** rather than static visuals."
    ],
    top_k: Annotated[int, "Number of top-matching video segments to retrieve based on event similarity."],
    list_video_id: Annotated[list[str], "List of video IDs to limit the event search domain (auto-provided)."],
    user_id: Annotated[str, "User identifier for context or permissions (auto-provided)."],
    metric_type: Annotated[str, "Metric type used for similarity computation in Milvus (auto-provided)."],
    param: Annotated[dict, "Additional Milvus or embedding parameters (auto-provided)."],
    milvus_client: Annotated[SegmentCaptionImageMilvusClient, "Milvus client for segment-level or event-level embedding search (auto-provided)."],
    external_client: Annotated[ExternalEncodeClient, "External encoding client for generating event embeddings from natural language queries (auto-provided)."],
    postgres_client: Annotated[PostgresClient, "Postgres client for retrieving related event or segment metadata (auto-provided)."],
    minio_client: Annotated[StorageClient, "Storage Client for reading event-level metadata stored in MinIO (auto-provided)."],
    output_fields: list[str] = ['id', 'related_video_name', 'related_video_id', 'segment_index', 'segment_minio_url', 'user_bucket', 'caption', 'start_time', 'end_time']
) -> list[tuple[float, SegmentObjectInterface]]:
    

    embedding_request = TextEmbeddingRequest(
        texts=[event_query],
        metadata={}
    )
    response = await external_client.encode_text(request=embedding_request)
    query_embedding = cast(list[list[float]], response.embeddings)

    filter_condition =SegmentCaptionFilterCondition(related_video_id=list_video_id, user_bucket=user_id)

    milvus_response = await milvus_client.search_dense(
        query_embedding=query_embedding,
        top_k=top_k,
        metric_type=metric_type,
        param=param,
        output_fields=output_fields,
        filter_expr=filter_condition
    )
    result = []
    for res in milvus_response:
        result.append(
            (
                res.score,
                SegmentObjectInterface(
                    related_video_id=res.related_video_id,
                    start_frame_index=res.start_frame,
                    end_frame_index=res.end_frame,
                    start_time=res.start_time,
                    end_time=res.end_time,
                    caption_info=res.caption
                )
            )
        )

    return result


