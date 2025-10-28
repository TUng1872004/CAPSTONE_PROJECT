import cv2
from pathlib import Path
from fastapi import UploadFile
from typing import BinaryIO
from fractions import Fraction
import ffmpeg 
import hashlib
def valid_video_files(file: UploadFile) -> bool:
    video_mime_types = {
        "video/mp4",
        "video/mpeg",
        "video/avi",
        "video/quicktime",   
        "video/x-msvideo",
        "video/x-ms-wmv",
        "video/x-flv",
        "video/webm",
        "video/3gpp",
        "video/3gpp2",
        "application/octet-stream",  
    }
    video_extensions = {
        ".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv",
        ".webm", ".3gp", ".mpeg", ".mpg"
    }

    content_type = (file.content_type or "").lower()
    filename = file.filename or ""

    if content_type not in video_mime_types and not any(filename.endswith(ext) for ext in video_extensions):
       return False
    return True


def get_video_metadata(video_filename: str, file: BinaryIO) -> dict:
    extension = Path(video_filename).suffix
    file.seek(0)
    import tempfile
    with tempfile.NamedTemporaryFile(delete=True, suffix=extension) as tmp:
        tmp.write(file.read())
        tmp.flush()

        probe = ffmpeg.probe(tmp.name)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None
        )
        if video_stream is None:
            return {}
        
        tmp.seek(0)
        md5 = hashlib.md5(tmp.read()).hexdigest()
        fps = float(Fraction(video_stream["avg_frame_rate"])) if "avg_frame_rate" in video_stream else None

        file.seek(0)
        return {
            "filename": video_filename,
            "codec": video_stream.get("codec_name"),
            "fps": fps,
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "size_bytes": int(probe["format"]["size"]),
            "checksum_md5": md5,
            'extension': extension
        }
    


def get_video_fps(video_path: str) -> float:
    """Return the FPS (frames per second) of a video file using OpenCV."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    return fps 