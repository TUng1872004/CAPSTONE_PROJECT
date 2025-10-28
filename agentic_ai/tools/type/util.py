"""
This file holds basic utilities to help agents recognize and convert between
video frames, timestamps, and durations.
"""
import asyncio
from datetime import datetime
import base64
import mimetypes
from typing import Tuple, cast
from agentic_ai.tools.schema.artifact import VideoObject, ImageObjectInterface, SegmentObjectInterface
from typing import Annotated
from agentic_ai.tools.clients.postgre.client import PostgresClient

from agentic_ai.tools.clients.minio.client import StorageClient
from collections import defaultdict
import re
from  urllib.parse import urlparse


def extract_s3_minio_url(s3_link:str) -> tuple[str,str]:
    parsed = urlparse(s3_link)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key


def frame_to_timecode(frame_index: int, fps: float) -> str:
    if fps <= 0:
        raise ValueError("FPS must be greater than zero.")
    total_seconds = frame_index / fps

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"



def timecode_to_frame(timecode: str, fps: float) -> int:
    """
    Convert a timecode string (HH:MM:SS.sss) into a frame index given a frame rate (FPS).

    Args:
        timecode (str): Timecode string, e.g., "00:01:23.456" or "01:10:05.003".
        fps (float): Frames per second. Must be > 0.

    Returns:
        int: The corresponding frame index (rounded to nearest integer).

    Raises:
        ValueError: If the timecode format is invalid or FPS <= 0.
    """
    if fps <= 0:
        raise ValueError("FPS must be greater than zero.")
    match = re.match(r"^(\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)$", timecode)
    if not match:
        raise ValueError(f"Invalid timecode format: '{timecode}'. Expected 'HH:MM:SS.sss'.")
    hours, minutes, seconds = match.groups()
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)    
    frame_index = round(total_seconds * fps)
    return frame_index




def organize_images(
        list_images: Annotated[list[ImageObjectInterface], "List of ImageObjectInterface"], 
        query:Annotated[str, "The query that you just search for"]) -> dict:
    """
    This function will return readable representation of ImageObjectInterface, which help you to better understand the results.
    """
    result_dict: dict[str, list[dict]] = defaultdict(list)
    
    for image in list_images:
        result_dict[image.related_video_id].append({
            "frame_index": image.frame_index,
            "timestamp": image.timestamp,
            "caption": image.caption_info,
            "score": round(image.score, 4),
            "minio_path": image.minio_path,
            "query_relation": f"Match for query: '{query}'"
        })
    
    readable_result = {
        "type": "visual_search_result",
        "query": query,
        "summary": f"Retrieved {len(list_images)} visually similar frames across {len(result_dict)} videos.",
        "results": result_dict
    }
    
    return readable_result


def organize_segments(
    list_segments: Annotated[list["SegmentObjectInterface"], "List of SegmentObjectInterface"], 
    query: Annotated[str, "The query that you just searched for"]
) -> dict:
    """
    Organize retrieved SegmentObjectInterface objects into a structured,
    descriptive, and interpretable representation grouped by their related video ID.

    This representation helps downstream agents or evaluators understand
    what parts of each video are most semantically relevant to the query.
    """

    result_dict: dict[str, list[dict]] = defaultdict(list)

    for segment in list_segments:
        result_dict[segment.related_video_id].append({
            "start_frame_index": segment.start_frame_index,
            "end_frame_index": segment.end_frame_index,
            "start_time": segment.start_time,
            "end_time": segment.end_time,
            "caption": segment.caption_info,
            "score": round(segment.score, 4),
            "duration": f"{segment.start_time} → {segment.end_time}",
            "query_relation": f"Segment semantically related to query: '{query}'"
        })

    for video_id in result_dict:
        result_dict[video_id].sort(key=lambda x: x["score"], reverse=True)

    readable_result = {
        "type": "visual_segment_search_result",
        "query": query,
        "summary": (
            f"Retrieved {len(list_segments)} relevant segments across "
            f"{len(result_dict)} videos based on semantic similarity to the query."
        ),
        "results": result_dict
    }

    return readable_result


def from_index_to_time(
    video: VideoObject,
    frame_index: int
) -> str:
    """
    Return the exact timestamp (in ISO 8601 format) for a given frame index.
    Args:
        video (VideoObject): The reference video object.
        frame_index (int): The frame index to convert.
    Returns:
        str: ISO-format timestamp corresponding to the frame position.
    """
    return frame_to_timecode(frame_index=frame_index, fps=video.fps)

    


def from_range_index_to_range_time(
    video: VideoObject,
    start_frame_index: int,
    end_frame_index: int
) -> Tuple[str, str]:
    """
    Convert a frame range into a corresponding time range.
    Args:
        video (VideoObject): The reference video object.
        start_frame_index (int): The first frame index in the range.
        end_frame_index (int): The last frame index in the range.
    Returns:
        Tuple[str, str]: Start and end timestamps (ISO 8601 format).
    """
    return frame_to_timecode(frame_index=start_frame_index, fps=video.fps),frame_to_timecode(frame_index=end_frame_index, fps=video.fps)






def from_time_to_index(
    video: VideoObject,
    time: str
) -> int:
    """
    Return the frame index corresponding to a given timestamp.
    Args:
        video (VideoObject): The reference video object.
        time (str): Timestamp in ISO 8601 format (e.g., '2025-10-24T12:34:56.789Z').
    Returns:
        int: Frame index closest to the given time.
    """
    return timecode_to_frame(timecode=time, fps=video.fps)
    


def from_range_time_to_range_index(
    video: VideoObject,
    start_time: str,
    end_time: str
) -> Tuple[int, int]:
    """
    Convert a time range into a corresponding frame index range.
    Args:
        video (VideoObject): The reference video object.
        start_time (str): Start timestamp in ISO 8601 format.
        end_time (str): End timestamp in ISO 8601 format.
    Returns:
        Tuple[int, int]: Start and end frame indices.
    """
    return timecode_to_frame(timecode=start_time, fps=video.fps), timecode_to_frame(timecode=start_time, fps=video.fps)




def read_image(image_interface: ImageObjectInterfaceter, minio_client: StorageClient) -> tuple[str, str]:
    """
    Read image, return base64 and mime/type
    """
    minio = image_interface.minio_path
    bucket, object_name = extract_s3_minio_url(minio)
    image_bytes = cast(bytes, minio_client.get_object(bucket=bucket, object_name=object_name))
    mime_type, _ = mimetypes.guess_type(object_name)
    mime_type = mime_type or "application/octet-stream"
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    return base64_str, mime_type


async def read_segment(
    segment_interface: SegmentObjectInterface, 
    minio_client: StorageClient, 
    postgre_client: PostgresClient
) -> Tuple[str, bytes]:
    """
    Fetch a video segment and return its extension and bytes.
    """

    video_artifact = await postgre_client.get_artifact(artifact_id=segment_interface.related_video_id)
    if video_artifact is None:
        raise ValueError(f"Video artifact with id {segment_interface.related_video_id} should exist but does not.")

    extension = (video_artifact.artifact_metadata or {}).get("extension")
    if not extension:
        raise KeyError(f"Missing 'extension' in artifact_metadata for {video_artifact.artifact_id}")

    video_url = video_artifact.minio_url
    bucket_video, object_video_name = extract_s3_minio_url(video_url)

    loop = asyncio.get_event_loop()
    video_bytes = await loop.run_in_executor(
        None,
        lambda: minio_client.get_object(bucket=bucket_video, object_name=object_video_name)
    )
    video_bytes = cast(bytes, video_bytes)
    return extension, video_bytes



     


async def get_related_asr(
    artifact: Annotated[ImageObjectInterface | SegmentObjectInterface, "Image or segment to contextualize with ASR."],
    window_seconds: Annotated[float, "Time window around artifact (± seconds for transcript snippet).", default=10.0],
    postgre_client: Annotated[PostgresClient, "Auto-provided."],
    minio_client: Annotated[StorageClient, "Auto-provided."],
):
    

async def link_artifacts_by_lineage(
    start_artifact_id: Annotated[str, "Starting artifact ID (e.g., image artifact_id)."],
    depth: Annotated[int, "Lineage traversal depth (default: 2).", default=2],
    filter_types: Annotated[list[str], "Artifact types to include (e.g., ['ImageArtifact', 'ASRArtifact']).", default=[]],
    postgre_client: Annotated[PostgresClient, "Auto-provided."],
) -> list[ArtifactMetadata]:
    




async def find_similar_moments(
    reference: ImageObjectInterface | SegmentObjectInterface,
    similarity_threshold: float = 0.8,
    search_scope: Annotated[Literal["same_video", "all_videos"], "Where to search"],
    **clients
) -> list[tuple[float, ImageObjectInterface | SegmentObjectInterface]]:
    """
    Find moments visually/semantically similar to a reference.
    Useful for finding repeated actions, similar scenes, or callbacks.
    """
    pass


