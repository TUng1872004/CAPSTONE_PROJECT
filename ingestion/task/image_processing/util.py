import asyncio
import cv2
import numpy as np
from urllib.parse import urlparse
from typing import Any, List, Tuple

def get_segment_frame_indices(start: int, end: int, n: int) -> list[int]:
    """Return n evenly spaced frame indices between start and end."""
    if n <= 0 or end <= start:
        return []
    total = end - start
    return [start + (i + 1) * total // (n + 1) for i in range(n)]



def parse_s3_url(s3_url: str) -> tuple[str, str]:
    parsed = urlparse(s3_url)
    return parsed.netloc, parsed.path.lstrip("/")

def read_frame_sync(video_path: str, frame_index: int) -> bytes:
    """Blocking: read a specific frame from a video and return it encoded as WebP."""
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_index < 0 or frame_index >= total:
        cap.release()
        raise ValueError(f"Frame index {frame_index} out of range (0-{total - 1})")

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()

    if not ok:
        raise RuntimeError(f"Failed to read frame at index {frame_index}")

    success, img = cv2.imencode(".webp", frame, [cv2.IMWRITE_WEBP_QUALITY, 90])
    if not success:
        raise RuntimeError(f"Failed to encode frame {frame_index} as WebP")

    return img.tobytes()


async def read_frame(video_path: str, frame_index: int) -> bytes:
    """Async wrapper for frame extraction by frame index."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_frame_sync, video_path, frame_index)


async def extract_frames_from_segments(
    video_path: str,
    segments: List[Tuple[int, int]],
    n_per_segment: int
) -> List[Tuple[int, bytes]]:
    all_indices = []
    for start, end in segments:
        all_indices.extend(
            get_segment_frame_indices(start,end, n_per_segment)
        )
    all_indices = sorted(set(all_indices))
    tasks = [read_frame(video_path, idx) for idx in all_indices]
    frames = await asyncio.gather(*tasks)

    return list(zip(all_indices, frames))