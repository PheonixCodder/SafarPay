"""S3 storage provider for the ride service.

Used exclusively for generating presigned PUT URLs for proof-of-service
image uploads and presigned GET URLs for proof image retrieval.

The actual binary is never touched by this service — S3 ↔ Client directly.
boto3 is run in a thread pool (asyncio.to_thread) because the AWS SDK
is synchronous.
"""
from __future__ import annotations

import asyncio
import logging
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from sp.core.config import get_settings

logger = logging.getLogger("ride.storage")

_DEFAULT_PUT_EXPIRES = 900   # 15 minutes — enough for a mobile upload
_DEFAULT_GET_EXPIRES = 3600  # 1 hour    — enough for display / audit


class S3StorageProvider:
    """Thread-safe S3 client wrapper for the ride service."""

    def __init__(self) -> None:
        settings = get_settings()
        region = settings.AWS_REGION
        self._bucket = settings.S3_PROOF_BUCKET
        self._s3 = boto3.client(
            "s3",
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        logger.info("S3StorageProvider initialised bucket=%s region=%s", self._bucket, region)

    # ------------------------------------------------------------------
    # Presigned PUT — client uploads directly
    # ------------------------------------------------------------------

    async def generate_presigned_put_url(
        self,
        object_key: str,
        *,
        content_type: str = "image/jpeg",
        expires_in: int = _DEFAULT_PUT_EXPIRES,
    ) -> str:
        """
        Return a presigned PUT URL the mobile client can use to upload a proof
        image directly to S3 without going through this service.

        Args:
            object_key:   The S3 key to pre-authorise (already constructed by caller).
            content_type: MIME type the client must set in the Content-Type header.
            expires_in:   Seconds until the URL expires (default 15 min).

        Returns:
            A fully-signed HTTPS URL string.

        Raises:
            RuntimeError: If boto3 cannot sign the request.
        """
        def _generate() -> str:
            return self._s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self._bucket,
                    "Key": object_key,
                },
                ExpiresIn=expires_in,
            )

        try:
            return await asyncio.to_thread(_generate)
        except ClientError as exc:
            logger.error("Failed to generate PUT presigned URL key=%s: %s", object_key, exc)
            raise RuntimeError(f"Could not generate upload URL: {exc}") from exc

    # ------------------------------------------------------------------
    # Presigned GET — serve image back to authorised callers
    # ------------------------------------------------------------------

    async def generate_presigned_get_url(
        self,
        object_key: str,
        *,
        expires_in: int = _DEFAULT_GET_EXPIRES,
    ) -> str:
        """
        Return a presigned GET URL so authorised clients can view/download
        a proof image without making the bucket public.

        Args:
            object_key: S3 key of the existing proof image.
            expires_in: Seconds until the URL expires (default 1 hour).

        Returns:
            A fully-signed HTTPS URL string.
        """
        def _generate() -> str:
            return self._s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )

        try:
            return await asyncio.to_thread(_generate)
        except ClientError as exc:
            logger.error("Failed to generate GET presigned URL key=%s: %s", object_key, exc)
            raise RuntimeError(f"Could not generate view URL: {exc}") from exc


def build_proof_key(ride_id: uuid.UUID, proof_type: str, filename: str | None = None) -> str:
    """
    Construct a deterministic, collision-resistant S3 object key for a proof image.

    Pattern:  rides/{ride_id}/proofs/{proof_type}/{uuid}.{ext}

    Args:
        ride_id:    UUID of the ride.
        proof_type: 'PICKUP' | 'DROPOFF' (matches domain ProofType enum value).
        filename:   Optional original filename — used only to extract the extension.

    Returns:
        A string S3 key, e.g.  rides/abc.../proofs/PICKUP/def....jpg
    """
    ext = "jpg"
    if filename:
        parts = filename.rsplit(".", 1)
        if len(parts) == 2 and parts[1].lower() in {"jpg", "jpeg", "png", "webp", "heic"}:
            ext = parts[1].lower()
    return f"rides/{ride_id}/proofs/{proof_type.upper()}/{uuid.uuid4().hex}.{ext}"
