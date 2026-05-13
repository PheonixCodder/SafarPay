from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sp.core.config import Settings

from ..domain.exceptions import (
    InsufficientWalletBalanceError,
    ReservationNotFoundError,
    WalletFrozenError,
)
from ..domain.models import PassengerPaymentMethod
from .schemas import (
    CaptureCommissionRequest,
    CollectionConfirmationRequest,
    CompleteRidePaymentRequest,
    CreateRidePaymentRequest,
    CreateSandboxCardRequest,
    CreateTopupRequest,
    EligibilityRequest,
    ReleaseCommissionRequest,
    ReserveCommissionRequest,
)


def _commission(basis_amount: float, rate: float) -> float:
    return round(float(basis_amount) * float(rate), 2)


class WalletUseCases:
    def __init__(self, repo, settings: Settings) -> None:
        self._repo = repo
        self._settings = settings

    async def get_or_create_wallet(self, driver_id: UUID):
        return await self._repo.get_or_create_wallet(driver_id)

    async def get_ledger(self, driver_id: UUID, limit: int = 50, offset: int = 0):
        wallet = await self._repo.get_or_create_wallet(driver_id)
        return await self._repo.list_ledger(wallet.id, limit=limit, offset=offset)

    async def create_topup(self, driver_id: UUID, req: CreateTopupRequest, idempotency_key: str):
        wallet = await self._repo.get_or_create_wallet(driver_id)
        topup = await self._repo.create_topup(wallet, req, idempotency_key)
        # Sandbox/dev behavior: provider succeeds immediately. Production adapters
        # should move this credit to signed callback/polling confirmation only.
        await self._repo.credit_topup(topup, idempotency_key=f"{idempotency_key}:credit")
        return topup


class PaymentMethodUseCases:
    def __init__(self, repo) -> None:
        self._repo = repo

    async def setup_intent(self, passenger_id: UUID) -> dict:
        return {
            "setup_intent_id": f"seti_{uuid4().hex}",
            "provider": "SANDBOX",
            "client_secret": f"sandbox_secret_{uuid4().hex}",
        }

    async def create_sandbox_card(self, passenger_id: UUID, req: CreateSandboxCardRequest):
        return await self._repo.create_card(passenger_id, req)

    async def list_methods(self, passenger_id: UUID):
        return await self._repo.list_payment_methods(passenger_id)

    async def set_active(self, passenger_id: UUID, method_id: UUID):
        return await self._repo.set_active_payment_method(passenger_id, method_id)

    async def delete(self, passenger_id: UUID, method_id: UUID) -> None:
        await self._repo.delete_payment_method(passenger_id, method_id)


class RidePaymentUseCases:
    def __init__(self, repo) -> None:
        self._repo = repo

    async def create_ride_payment(self, ride_id: UUID, req: CreateRidePaymentRequest, idempotency_key: str):
        if req.passenger_payment_method == PassengerPaymentMethod.CARD:
            if not req.passenger_payment_method_id:
                raise ValueError("passenger_payment_method_id is required for CARD payments.")
            method = await self._repo.find_active_payment_method(
                req.passenger_id, req.passenger_payment_method_id
            )
            if not method:
                raise ValueError("Active card payment method not found.")
            return await self._repo.create_card_ride_payment(ride_id, req, method, idempotency_key)
        return await self._repo.create_driver_collected_ride_payment(ride_id, req, idempotency_key)

    async def capture_payment_intent(self, ride_id: UUID, payment_intent_id: UUID, amount_final: float, idempotency_key: str):
        return await self._repo.capture_payment_intent(ride_id, payment_intent_id, amount_final, idempotency_key)

    async def complete_ride_payment(self, ride_id: UUID, req: CompleteRidePaymentRequest, idempotency_key: str):
        payment = await self._repo.find_ride_payment(ride_id)
        if not payment:
            raise ValueError("Ride payment not found.")
        if payment.passenger_payment_method == PassengerPaymentMethod.CARD:
            if not payment.payment_intent_id:
                raise ValueError("Card ride payment is missing a payment intent.")
            await self._repo.capture_payment_intent(
                ride_id,
                payment.payment_intent_id,
                req.final_amount,
                idempotency_key,
            )
            return await self._repo.find_ride_payment(ride_id)
        return await self._repo.mark_driver_collected_unconfirmed(
            ride_id,
            req.driver_id,
            req.final_amount,
            idempotency_key,
            req.correlation_id,
        )

    async def get_ride_payment(self, ride_id: UUID):
        return await self._repo.find_ride_payment(ride_id)

    async def confirm_collection(self, ride_id: UUID, req: CollectionConfirmationRequest, idempotency_key: str):
        return await self._repo.confirm_driver_collection(ride_id, req, idempotency_key)


class CommissionUseCases:
    def __init__(self, repo, settings: Settings) -> None:
        self._repo = repo
        self._settings = settings

    async def check_eligibility(self, driver_id: UUID, req: EligibilityRequest):
        policy = await self._repo.get_active_policy(default_rate=self._settings.DRIVER_COMMISSION_RATE)
        required = _commission(req.basis_amount, float(policy.rate))
        wallet = await self._repo.get_or_create_wallet(driver_id)
        if wallet.status.value == "FROZEN":
            return False, "WALLET_FROZEN", wallet, required
        if float(wallet.reserved_balance) + required > float(wallet.max_reserved_limit):
            return False, "DRIVER_RESERVATION_LIMIT_EXCEEDED", wallet, required
        if float(wallet.available_balance) - required < -float(wallet.negative_limit):
            return False, "INSUFFICIENT_DRIVER_WALLET_BALANCE", wallet, required
        return True, None, wallet, required

    async def reserve(self, ride_id: UUID, req: ReserveCommissionRequest, idempotency_key: str):
        policy = await self._repo.get_active_policy(default_rate=self._settings.DRIVER_COMMISSION_RATE)
        commission = _commission(req.basis_amount, float(policy.rate))
        wallet = await self._repo.get_or_create_wallet(req.driver_id)
        if wallet.status.value == "FROZEN":
            raise WalletFrozenError("WALLET_FROZEN")
        if float(wallet.reserved_balance) + commission > float(wallet.max_reserved_limit):
            raise InsufficientWalletBalanceError("DRIVER_RESERVATION_LIMIT_EXCEEDED")
        if float(wallet.available_balance) - commission < -float(wallet.negative_limit):
            raise InsufficientWalletBalanceError("INSUFFICIENT_DRIVER_WALLET_BALANCE")
        return await self._repo.reserve_commission(
            ride_id,
            req.driver_id,
            wallet,
            policy,
            req.basis_amount,
            commission,
            req.currency,
            datetime.now(timezone.utc) + timedelta(hours=self._settings.PAYMENT_RESERVATION_EXPIRY_HOURS),
            idempotency_key,
            req.correlation_id,
        )

    async def capture(self, ride_id: UUID, req: CaptureCommissionRequest, idempotency_key: str):
        reservation = await self._repo.find_active_reservation(ride_id, req.driver_id)
        if not reservation:
            raise ReservationNotFoundError("Active commission reservation not found.")
        policy_rate = float(reservation.rate_snapshot)
        actual_commission = _commission(req.final_amount, policy_rate)
        return await self._repo.capture_commission(
            reservation,
            req.final_amount,
            actual_commission,
            idempotency_key,
            req.correlation_id,
        )

    async def release(self, ride_id: UUID, req: ReleaseCommissionRequest, idempotency_key: str):
        reservation = await self._repo.find_active_reservation(ride_id, req.driver_id)
        if not reservation:
            return None
        return await self._repo.release_commission(reservation, idempotency_key, req.correlation_id, req.reason)

    async def expire_stale(self) -> int:
        return await self._repo.expire_stale_reservations()
