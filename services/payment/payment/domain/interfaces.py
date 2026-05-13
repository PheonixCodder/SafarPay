from __future__ import annotations

from typing import Protocol
from uuid import UUID


class ProviderAdapterProtocol(Protocol):
    async def create_setup_intent(self, passenger_id: UUID) -> dict:
        ...

    async def charge(self, payment_method_token: str, amount: float, currency: str, idempotency_key: str) -> dict:
        ...
