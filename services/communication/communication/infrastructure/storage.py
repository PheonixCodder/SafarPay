"""S3 storage provider for communication media."""
from __future__ import annotations

import asyncio
import logging
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from sp.core.config import get_settings

logger = logging.getLogger("communication.storage")


class S3StorageProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.S3_COMMUNICATION_BUCKET
        self._s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            config=Config(signature_version="s3v4"),
        )

    async def generate_presigned_put_url(
        self,
        object_key: str,
        *,
        content_type: str,
        expires_in: int = 900,
    ) -> str:
        def _generate() -> str:
            return self._s3.generate_presigned_url(
                "put_object",
                Params={"Bucket": self._bucket, "Key": object_key, "ContentType": content_type},
                ExpiresIn=expires_in,
            )

        try:
            return await asyncio.to_thread(_generate)
        except ClientError as exc:
            logger.error("Failed to generate communication media PUT URL key=%s: %s", object_key, exc)
            raise RuntimeError(f"Could not generate upload URL: {exc}") from exc

    async def generate_presigned_get_url(self, object_key: str, *, expires_in: int = 3600) -> str:
        def _generate() -> str:
            return self._s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )

        try:
            return await asyncio.to_thread(_generate)
        except ClientError as exc:
            logger.error("Failed to generate communication media GET URL key=%s: %s", object_key, exc)
            raise RuntimeError(f"Could not generate view URL: {exc}") from exc


def build_media_key(conversation_id: uuid.UUID, media_type: str, filename: str | None = None) -> str:
    ext = "bin"
    allowed = {
        "jpg", "jpeg", "png", "webp", "heic",
        "mp3", "m4a", "aac", "ogg", "oga", "webm", "mp4",
    }
    if filename:
        parts = filename.rsplit(".", 1)
        if len(parts) == 2 and parts[1].lower() in allowed:
            ext = parts[1].lower()
    return f"conversations/{conversation_id}/{media_type.lower()}/{uuid.uuid4().hex}.{ext}"
