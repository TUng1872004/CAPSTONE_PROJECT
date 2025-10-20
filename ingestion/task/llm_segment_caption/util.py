import cv2
import numpy as np
from typing import List
from urllib.parse import urlparse


def return_related_asr_with_shot(
    asr_tokens: list[dict],
    start_frame: int,
    end_frame: int,
    *,
    overlap_threshold: float = 0.8,
)-> str:
    """
    Return the concatenated related asr moment, based on the segments
    """

    result = []

    for token in asr_tokens:
        token_start = int(token.get("start_frame", 0))
        token_end = int(token.get("end_frame", 0))
        token_text = token.get("text", "").strip()

        if not token_text or token_end <= token_start:
            continue
        
        intersection = max(
            0, min(
                token_end, end_frame
            ) - max(token_start, start_frame)
        )

        token_length = token_end - token_start
        overlap_ratio = intersection / token_length

        fully_inside = token_start >= start_frame and token_end <= end_frame

        if fully_inside or overlap_ratio >= overlap_threshold:
            result.append(token_text)
    
    return "\n\n".join(result).strip()


import cv2
import base64
import numpy as np
from typing import List


def extract_images(
    local_video_path: str,
    start_frame: int,
    end_frame: int,
    n_frames: int,
    *,
    quality: int = 80,
) -> List[str]:
    """
    Extract `n_frames` uniformly spaced frames between [start_frame, end_frame)
    and return them as base64-encoded WEBP strings.

    Args:
        local_video_path: Path to the video file.
        start_frame: Starting frame index (inclusive).
        end_frame: Ending frame index (exclusive).
        n_frames: Number of frames to sample uniformly.
        quality: WEBP encoding quality (1–100), default 80.

    Returns:
        List of base64-encoded WEBP strings.
    """
    if n_frames <= 0 or end_frame <= start_frame:
        return []

    cap = cv2.VideoCapture(local_video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {local_video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    end_frame = min(end_frame, total_frames - 1)

    # Evenly spaced frame indices
    step = (end_frame - start_frame) / (n_frames + 1)
    frame_indices = [int(start_frame + (i + 1) * step) for i in range(n_frames)]

    encoded_frames: List[str] = []

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            print(f"[WARN] Could not read frame {idx}")
            continue

        # Encode to WEBP
        success, buffer = cv2.imencode(".webp", frame, [cv2.IMWRITE_WEBP_QUALITY, quality])
        if not success:
            print(f"[WARN] Failed to encode frame {idx}")
            continue

        # Convert to base64 string
        encoded = base64.b64encode(buffer).decode("utf-8")
        encoded_frames.append(encoded)

    cap.release()
    return encoded_frames



def parse_s3_url(s3_url: str) -> tuple[str, str]:
    parsed = urlparse(s3_url)
    return parsed.netloc, parsed.path.lstrip("/")
