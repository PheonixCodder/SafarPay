from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx
import pytest
from bidding.infrastructure.clients import PaymentClient


class FakeJsonResponse:
    status_code = 200
    content = b"{}"
    text = "{}"

    def json(self) -> dict[str, Any]:
        return {"reserved": True}


class FlakyPostClient:
    def __init__(self) -> None:
        self.calls = 0

    async def post(self, path: str, *, json: dict[str, Any], headers: dict[str, str]) -> FakeJsonResponse:
        self.calls += 1
        if self.calls == 1:
            raise httpx.ConnectError("payment unavailable")
        return FakeJsonResponse()


@pytest.mark.asyncio
async def test_payment_client_retries_transient_commission_reserve_connection_failure() -> None:
    payment = PaymentClient("http://payment:8000")
    fake_http = FlakyPostClient()
    payment._client = fake_http  # type: ignore[assignment]

    result = await payment.reserve_commission(
        ride_id=uuid4(),
        driver_id=uuid4(),
        passenger_id=uuid4(),
        basis_amount=620,
        idempotency_key="accept-bid-test",
    )

    assert result == {"reserved": True}
    assert fake_http.calls == 2
