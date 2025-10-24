"""
This file will contains the tools for agents to interact with the database
"""
from agent.tools.schema.artifact import VideoObject, SegmentObject, ImageObject









def get_videos_from_user(user_id: str) -> list[VideoObject]:
    """
    From the user id, return all the related videos
    """



def get_video(video_ids: list[str]) -> list[VideoObject]:
    """
    Return the corresponding objects, given the list of video ids
    Args:
        video_ids: list[str]
    Returns:
        list[VideoObject] 
    """


def return_extracted_images_from_segment(segment: SegmentObject) -> list[ImageObject]:
    """
    
    """


def return_related_segments_from_images(list_images: list[ImageObject]) -> list[SegmentObject]:
    """
    Given 
    """


def get_segments_from_videos_frame_index(
    first_frame_index:int,
    last_frame_index:int,
    video_id: str
) -> list[SegmentObject]:
    """
    Given a reference id of a video, and the timestamp in frame index (frame start, frame end), return the intersection segments. A segment that partially or totally overlap with the timestamp will be returned.
    """



def get_relative_time_duration(
    first_frame_index:int,
    last_frame_index:int,
    video_id: str
) -> str:
    """
    Return the duration of the segment in datetime isoformat
    """




