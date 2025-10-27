from __future__ import annotations

import json
from datetime import timedelta
from io import BytesIO
from typing import Any, BinaryIO, Dict, Generator, Optional
from loguru import logger
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel, Field


class MinioSettings(BaseModel):
    public_endpoint: str = Field(default="localhost:9000", description="Public endpoint for clients outside Docker")
    internal_endpoint: str = Field(default="minio:9000", description="Endpoint for containers inside Docker")
    access_key: str = Field(default="minioadmin", description="MinIO access key")
    secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    secure: bool = Field(default=False, description="Whether to use HTTPS when contacting MinIO")
    videos_bucket: str = Field(default="videos", description="Bucket used to persist original uploads")
    artifacts_bucket: str = Field(default="video-artifacts", description="Bucket used to persist derived outputs")
    manifest_prefix: str = Field(default="manifests", description="Prefix for run manifest objects")

    @property
    def scheme(self) -> str:
        return "https" if self.secure else "http"

    def get_url(self, internal: bool = False) -> str:
        endpoint = self.internal_endpoint if internal else self.public_endpoint
        return f"{self.scheme}://{endpoint}"


class StorageError(RuntimeError):
    """Raised when MinIO storage operations fail."""
    pass


class StorageClient:
    def __init__(self, settings: MinioSettings) -> None:
        self.minio_settings = settings
        self.client = Minio(
            self.minio_settings.internal_endpoint,
            access_key=self.minio_settings.access_key,
            secret_key=self.minio_settings.secret_key,
            secure=self.minio_settings.secure,
        )

    def _ensure_bucket(self, bucket: str) -> None:
        try:
            if not self.client.bucket_exists(bucket):
                logger.info(f"Bucket '{bucket}' does not exist — creating.")
                self.client.make_bucket(bucket)
        except S3Error as exc:
            logger.error(f"MinIO bucket check failed for '{bucket}': {exc}")
            raise StorageError(f"Failed to ensure bucket {bucket}: {exc}") from exc

    def upload_fileobj(
        self,
        bucket: str,
        object_name: str,
        file_obj: BinaryIO,
        *,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload a file-like object to the specified bucket and return an S3 URI."""

        self._ensure_bucket(bucket)
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=file_obj,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=content_type,
                metadata=metadata or None,  # type: ignore
            )
            uri = f"s3://{bucket}/{object_name}"
            logger.info(f"Uploaded object {uri}")
            return uri
        except S3Error as exc:
            logger.exception(f"Failed to upload {object_name} to bucket {bucket}: {exc}")
            raise StorageError(f"Upload failed for {object_name}: {exc}") from exc

    def put_json(
        self,
        bucket: str,
        object_name: str,
        payload: Dict[str, Any],
        *,
        content_type: str = "application/json",
    ) -> str:
        buffer = BytesIO(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        return self.upload_fileobj(
            bucket,
            object_name,
            buffer,
            content_type=content_type,
            metadata={"Content-Type": content_type},
        )

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        *,
        expires_seconds: timedelta = timedelta(seconds=3600),
        internal: bool = False,
    ) -> str:
        self._ensure_bucket(bucket)
        try:
            url = self.client.presigned_get_object(bucket, object_name, expires=expires_seconds)
            logger.debug(f"Generated presigned URL for {bucket}/{object_name}")
            return url
        except S3Error as exc:
            logger.exception(f"Failed to generate presigned URL for {bucket}/{object_name}: {exc}")
            raise StorageError(f"Failed to presign object {bucket}/{object_name}: {exc}") from exc

    def list_objects(self, bucket: str, prefix: Optional[str] = None) -> Generator[str, None, None]:
        """Yield object names (strings) from the given bucket."""
        self._ensure_bucket(bucket)
        try:
            for obj in self.client.list_objects(bucket, prefix=prefix or "", recursive=True):
                if obj.object_name:
                    yield obj.object_name
        except S3Error as exc:
            logger.exception(f"Failed to list objects for {bucket}/{prefix}: {exc}")
            raise StorageError(f"Failed to list objects: {exc}") from exc

    def get_object(self, bucket: str, object_name: str) -> bytes:
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
            logger.exception(f"Failed to fetch object {bucket}/{object_name}: {exc}")
            raise StorageError(f"Failed to fetch object {bucket}/{object_name}: {exc}") from exc

    def read_json(self, bucket: str, object_name: str) -> Dict[str, Any]:
        raw = self.get_object(bucket, object_name)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise StorageError(f"Stored object {bucket}/{object_name} is not valid JSON: {exc}") from exc

    def object_exists(self, bucket: str, object_name: str) -> bool:
        self._ensure_bucket(bucket)
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error as exc:
            if getattr(exc, "code", None) in ("NoSuchKey", "NoSuchObject"):
                return False
            raise StorageError(f"Error checking object {bucket}/{object_name}: {exc}") from exc
