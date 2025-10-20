from prefect import task
from prefect.cache_policies import CacheKeyFnPolicy
from prefect.context import TaskRunContext
from prefect.transactions import IsolationLevel
from prefect.locking.memory  import MemoryLockManager
import hashlib
from pathlib import Path

from typing import cast
from fastapi import UploadFile



def video_cache_key(context: TaskRunContext, parameters: dict) -> str:
    video_upload: UploadFile = parameters['video_upload']
    
    filename = cast(str, video_upload.filename) # ensure filename exist, already check in the preprocess
    content_type = video_upload.content_type or "unknown"

    video_upload.file.seek(0)
    checksum = hashlib.md5(video_upload.file.read()).hexdigest()
    video_upload.file.seek(0)
    video_name = Path(filename).stem

    return f"{video_name}-{checksum}-{content_type}"



per_video_cache_policy = CacheKeyFnPolicy(cache_key_fn=video_cache_key).configure(
    isolation_level=IsolationLevel.SERIALIZABLE,
    lock_manager=MemoryLockManager()
)

