from functools import lru_cache
from fastapi import Request
from core.pipeline.tracker import ArtifactTracker
from core.storage import StorageClient
from core.management.cleanup import ArtifactDeleter


@lru_cache(maxsize=1)
def get_artifact_tracker(request: Request) -> ArtifactTracker:
    return request.app.state.artifact_tracker

@lru_cache(maxsize=1)
def get_storage_client(request: Request) -> StorageClient:
    return request.app.state.storage_client



@lru_cache(maxsize=1)
def get_artifact_deleter(request: Request) -> ArtifactDeleter:
    tracker = get_artifact_tracker(request)#type:ignore
    storage_client = get_storage_client(request)#type:ignore
    return ArtifactDeleter(tracker, storage_client)




