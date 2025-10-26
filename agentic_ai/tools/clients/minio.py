import urllib3
from urllib3.util import Timeout
from minio import Minio, S3Error
from pydantic import BaseModel, Field, computed_field
import json
from typing import Iterable


class MinioSettings(BaseModel):  
    port: str
    host: str
    user:str
    password: str
    access_key: str = Field(default="minioadmin", description="MinIO access key")
    secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    secure: bool = Field(default=False, description="Whether to use HTTPS when contacting MinIO")

    @computed_field
    @property
    def endpoint(self) -> str:
        scheme = "https" if self.secure else "http"
        return f"{scheme}://{self.host}:{self.port}"
    



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
    
    def _ensure_bucket(self, bucket: str) -> None:
        try:
            if not self.client.bucket_exists(bucket):
                logger.info(f"Bucket named: {bucket} does not exist, creating")
                self.client.make_bucket(bucket)
        except S3Error as exc:
            logger.error("MinIO bucket check failed for %s: %s", bucket, exc)
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
            logger.info(f"Bucket: {bucket} has no {object_name}")
            return None
    
    def list_objects(self, bucket: str, prefix: str | None = None) -> Iterable[str]:
        self._ensure_bucket(bucket)
        try:
            for obj in self.client.list_objects(bucket, prefix=prefix or "", recursive=True):
                if obj.object_name is not None:
                    yield obj.object_name
        except S3Error as exc:
            logger.exception("Failed to list objects for %s/%s", bucket, prefix)
            raise StorageError(f"Failed to list objects: {exc}") from exc
    
    def read_json(self, bucket: str, object_name: str) -> Dict[str, Any] | None:
        raw = self.get_object(bucket, object_name)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise StorageError(f"Stored object {bucket}/{object_name} is not valid JSON: {exc}") from exc

    def object_exists(self, bucket:str, object_name: str) -> bool:
        self._ensure_bucket(bucket)
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error as exc:
            if exc.code in ("NoSuchKey", "NoSuchObject"):
                return False
            raise StorageError(f"Error checking object {bucket}/{object_name}: {exc}") from exc