import tempfile
import requests
from urllib.parse import urlparse




def resolve_video_url(video_url: str) -> str:
    parsed = urlparse(video_url)
    if parsed.scheme in {"http", "https"}:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                tmp.write(chunk)
        tmp.close()
        return tmp.name
    return video_url