import tempfile
from core.storage import StorageClient
from urllib.parse import urlparse
import asyncio





def parse_s3_url(s3_url: str) -> tuple[str, str]:
    parsed = urlparse(s3_url)
    return parsed.netloc, parsed.path.lstrip("/")





async def fetch_object_from_s3(s3_url: str, storage: StorageClient, suffix: str) -> str:
    """Fetch s3://bucket/path.mp4 to a local temp file asynchronously."""
    bucket, object_name = parse_s3_url(s3_url)
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, lambda: storage.get_object(bucket, object_name))
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(data)
    tmp.flush()
    tmp.close()
    return tmp.name


async def fetch_object_from_s3_bytes(s3_url: str, storage: StorageClient) -> bytes:
    bucket, object_name = parse_s3_url(s3_url)
    loop = asyncio.get_running_loop()

    data = await loop.run_in_executor(
        None,
        lambda: storage.get_object(bucket, object_name)
    )

    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"Expected bytes from storage.get_object, got {type(data)}")

    return data