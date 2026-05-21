"""Development OTP provider that writes OTP codes to service logs."""
from __future__ import annotations

import logging

from auth.domain.interfaces import OTPProviderProtocol

logger = logging.getLogger("auth.messaging.console")


class ConsoleOTPProvider(OTPProviderProtocol):
    """Print OTP codes for local development without external WhatsApp APIs."""

    async def send_otp(self, phone: str, code: str) -> None:
        masked_phone = f"****{phone[-4:]}" if len(phone) >= 4 else "****"
        logger.warning("DEV OTP for %s: %s", masked_phone, code)
