"""Google id_token verifier for mobile SDK flow.

The mobile app uses Google Sign-In SDK to get an id_token,
then sends it to the backend for offline verification.
No server-side redirect or code exchange needed.
"""
from __future__ import annotations

import asyncio
import logging

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from auth.domain.interfaces import GoogleTokenVerifierProtocol

logger = logging.getLogger("auth.security.google")


class GoogleTokenVerifier(GoogleTokenVerifierProtocol):
    """Verify Google id_tokens offline using google-auth library."""

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    async def verify(self, token: str) -> dict:
        """Verify a Google id_token and return user claims.

        Returns dict with keys: sub, email, name, picture, email_verified.
        Raises ValueError if token is invalid or email not verified.
        """
        # google-auth is synchronous — wrap to avoid blocking event loop
        claims = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            token,
            google_requests.Request(),
            self.client_id,
        )

        if not claims.get("email_verified", False):
            raise ValueError("Google email is not verified")

        logger.info(
            "Google token verified",
            extra={"sub": claims.get("sub"), "email": claims.get("email")},
        )

        return claims