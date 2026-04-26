"""Storage provider implementation using AWS S3."""
from __future__ import annotations

import asyncio
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from sp.core.config import get_settings
from ..domain.interfaces import StorageProviderProtocol

logger = logging.getLogger("verification.storage")


class S3StorageProvider(StorageProviderProtocol):
    def __init__(self) -> None:
        self.settings = get_settings()
        # Ensure AWS region is loaded from config, falling back to 'us-east-1' if missing.
        region = getattr(self.settings, "AWS_REGION", "us-east-1")
        self.s3_client = boto3.client(
            "s3",
            region_name=region,
            config=Config(signature_version="s3v4"),
        )

    async def generate_presigned_put_url(
        self, bucket_name: str, object_key: str, expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL to upload an object to S3 via a PUT request.
        """
        try:
            response = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            # In a real app we might log the exception or wrap it in a domain exception.
            raise RuntimeError(f"Could not generate presigned URL: {e}") from e

        return response

    async def get_object_bytes(self, bucket_name: str, object_key: str) -> bytes:
        """Fetch an object's bytes directly from S3."""
        def _fetch():
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            return response["Body"].read()

        try:
            return await asyncio.to_thread(_fetch)
        except ClientError as e:
            raise RuntimeError(f"Could not fetch object {object_key} from bucket {bucket_name}: {e}") from e

    async def delete_object(self, bucket_name: str, object_key: str) -> None:
        """Delete an object from S3."""
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object, Bucket=bucket_name, Key=object_key
            )
        except ClientError as e:
            # We don't necessarily want to crash the whole flow if cleanup fails, 
            # but we should log it.
            logger.error(f"Failed to delete old object {object_key} from {bucket_name}: {e}")
