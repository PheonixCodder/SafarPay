from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger("ride.payment_client")


class PaymentClient:
    def __init__(self, base_url: str, *, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout)
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _post(self, path: str, payload: dict[str, Any], idempotency_key: str) -> dict[str, Any] | None:
        if not self._client:
            logger.warning("PaymentClient not started; skipping path=%s", path)
            return None
        resp = await self._client.post(path, json=payload, headers={"Idempotency-Key": idempotency_key})
        if resp.status_code >= 400:
            detail = resp.text[:500]
            raise RuntimeError(f"Payment service rejected {path}: HTTP {resp.status_code} {detail}")
        if not resp.content:
            return None
        return resp.json()

    async def create_ride_payment(
        self,
        ride_id: UUID,
        passenger_id: UUID,
        passenger_payment_method: str,
        passenger_payment_method_id: UUID | None,
        amount_estimated: float | None,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return await self._post(
            f"/api/v1/internal/rides/{ride_id}/payments",
            {
                "passenger_id": str(passenger_id),
                "passenger_payment_method": passenger_payment_method,
                "passenger_payment_method_id": str(passenger_payment_method_id) if passenger_payment_method_id else None,
                "amount_estimated": amount_estimated,
                "currency": "PKR",
            },
            idempotency_key,
        ) or {}

    async def reserve_commission(
        self,
        ride_id: UUID,
        driver_id: UUID,
        passenger_id: UUID | None,
        basis_amount: float,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return await self._post(
            f"/api/v1/internal/rides/{ride_id}/commission/reserve",
            {
                "driver_id": str(driver_id),
                "passenger_id": str(passenger_id) if passenger_id else None,
                "basis_amount": basis_amount,
                "currency": "PKR",
            },
            idempotency_key,
        ) or {}

    async def capture_commission(
        self,
        ride_id: UUID,
        driver_id: UUID,
        final_amount: float,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return await self._post(
            f"/api/v1/internal/rides/{ride_id}/commission/capture",
            {"driver_id": str(driver_id), "final_amount": final_amount, "currency": "PKR"},
            idempotency_key,
        ) or {}

    async def complete_ride_payment(
        self,
        ride_id: UUID,
        driver_id: UUID,
        final_amount: float,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return await self._post(
            f"/api/v1/internal/rides/{ride_id}/payments/complete",
            {"driver_id": str(driver_id), "final_amount": final_amount, "currency": "PKR"},
            idempotency_key,
        ) or {}

    async def release_commission(
        self,
        ride_id: UUID,
        driver_id: UUID | None,
        reason: str | None,
        *,
        idempotency_key: str,
    ) -> dict[str, Any] | None:
        return await self._post(
            f"/api/v1/internal/rides/{ride_id}/commission/release",
            {"driver_id": str(driver_id) if driver_id else None, "reason": reason},
            idempotency_key,
        )


class NullPaymentClient:
    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def create_ride_payment(self, *args, **kwargs) -> dict[str, Any]:
        logger.warning("NullPaymentClient: create_ride_payment skipped")
        return {}

    async def reserve_commission(self, *args, **kwargs) -> dict[str, Any]:
        logger.warning("NullPaymentClient: reserve_commission skipped")
        return {}

    async def capture_commission(self, *args, **kwargs) -> dict[str, Any]:
        logger.warning("NullPaymentClient: capture_commission skipped")
        return {}

    async def complete_ride_payment(self, *args, **kwargs) -> dict[str, Any]:
        logger.warning("NullPaymentClient: complete_ride_payment skipped")
        return {}

    async def release_commission(self, *args, **kwargs) -> dict[str, Any] | None:
        logger.warning("NullPaymentClient: release_commission skipped")
        return None
