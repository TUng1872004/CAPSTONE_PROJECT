"""
This file holds basic utilities to help agents recognize and convert between
video frames, timestamps, and durations.
"""

from datetime import datetime
from typing import Tuple
from agent.tools.schema.artifact import VideoObject


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
    return NotImplemented


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
    return NotImplemented


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
    return NotImplemented


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
    return NotImplemented
