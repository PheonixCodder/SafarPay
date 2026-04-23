"""OTP rate limiting via Redis.

Uses CacheManager.increment() (atomic Redis INCR) for distributed,
race-condition-free rate limiting.
"""
from __future__ import annotations

from sp.infrastructure.cache.manager import CacheManager

from auth.domain.exceptions import OTPRateLimitError


class OTPRateLimiter:
    """Per-phone send limiting and per-IP verify limiting."""

    SEND_NAMESPACE = "otp_send_limit"
    VERIFY_NAMESPACE = "otp_verify_limit"

    SEND_MAX_PER_PHONE = 3       # max 3 OTPs per phone per window
    SEND_WINDOW_SECONDS = 900    # 15-minute window
    VERIFY_MAX_PER_IP = 10       # max 10 verify attempts per IP per window
    VERIFY_WINDOW_SECONDS = 900  # 15-minute window

    def __init__(self, cache: CacheManager) -> None:
        self.cache = cache

    async def check_send_limit(self, phone: str) -> None:
        """Raise OTPRateLimitError if phone has exceeded send limit."""
        count = await self.cache.increment(
            self.SEND_NAMESPACE, phone, ttl=self.SEND_WINDOW_SECONDS
        )
        if count > self.SEND_MAX_PER_PHONE:
            raise OTPRateLimitError(
                f"Too many OTP requests. Try again in {self.SEND_WINDOW_SECONDS // 60} minutes."
            )

    async def check_verify_limit(self, ip_address: str) -> None:
        """Raise OTPRateLimitError if IP has exceeded verify limit."""
        count = await self.cache.increment(
            self.VERIFY_NAMESPACE, ip_address, ttl=self.VERIFY_WINDOW_SECONDS
        )
        if count > self.VERIFY_MAX_PER_IP:
            raise OTPRateLimitError(
                "Too many verification attempts. Try again later."
            )
