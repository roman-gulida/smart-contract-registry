"""
S3-compatible object storage service (SeaweedFS)
Handles PDF upload, download, and bucket management via boto3.
"""
import logging

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY or "ignored",
            aws_secret_access_key=settings.S3_SECRET_KEY or "ignored",
            region_name=settings.S3_REGION,
            config=BotoConfig(signature_version="s3v4"),
        )
        self._bucket = settings.S3_BUCKET_NAME

    # Bucket management
    def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't already exist."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
            logger.info("S3 bucket '%s' already exists.", self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)
            logger.info("Created S3 bucket '%s'.", self._bucket)

    # Object operations
    def upload_file(
        self, key: str, data: bytes, content_type: str = "application/pdf"
    ) -> str:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        logger.info("Uploaded object '%s' to bucket '%s'.", key, self._bucket)
        return key

    def download_file(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError as exc:
            logger.error("Failed to download '%s': %s", key, exc)
            raise FileNotFoundError(
                f"Object '{key}' not found in bucket '{self._bucket}'."
            ) from exc

    def file_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def delete_file(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)
        logger.info("Deleted object '%s' from bucket '%s'.", key, self._bucket)

    @staticmethod
    def get_object_key(doc_hash: str) -> str:
        return f"{doc_hash.removeprefix('0x')}.pdf"


# Singleton + FastAPI dependency
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
