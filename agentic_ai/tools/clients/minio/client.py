from ingestion.core.config.storage import MinioSettings
import urllib3
from urllib3.util import Timeout
from minio import Minio
from minio.error import S3Error
from typing import Dict, Any
import json


import logging


class StorageError(RuntimeError):
    """Raised when MinIO storage operations fail."""
    pass

class StorageClient:
    def __init__(self, settings: MinioSettings ) -> None:
        self.settings = settings 
        timeout = Timeout(connect=5.0, read=120.0)  
        self._http_client = urllib3.PoolManager(
            maxsize=50,
            timeout=timeout,
            block=True,
        )
        self.client = Minio(
            endpoint=f"{settings.host}:{settings.port}",
            access_key=settings.access_key,
            secret_key=settings.secret_key,
            secure=settings.secure,
            http_client=self._http_client,
        )

        self.logger = logging.getLogger(__name__)
    
    def _ensure_bucket(self, bucket: str) -> None:
        try:
            if not self.client.bucket_exists(bucket):
                self.logger.info(f"Bucket named: {bucket} does not exist, creating")
                self.client.make_bucket(bucket)
        except S3Error as exc:
            self.logger.error("MinIO bucket check failed for %s: %s", bucket, exc)
            raise StorageError(f"Failed to ensure bucket {bucket}: {exc}") from exc



    def get_object(self, bucket: str, object_name: str) -> bytes | None:
        self._ensure_bucket(bucket)
        try:
            response = self.client.get_object(bucket, object_name)
            try:
                data = response.read()
                return data
            finally:
                response.close()
                response.release_conn()
        except S3Error as exc:
            self.logger.info(f"Bucket: {bucket} has no {object_name}")
            return None

    def read_json(self, bucket: str, object_name: str) -> Dict[str, Any] | None:
        raw = self.get_object(bucket, object_name)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise StorageError(f"Stored object {bucket}/{object_name} is not valid JSON: {exc}") from exc