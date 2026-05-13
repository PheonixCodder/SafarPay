from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.schemas import (
    CollectionConfirmationRequest,
    CreateRidePaymentRequest,
    CreateSandboxCardRequest,
    CreateTopupRequest,
)
from .orm_models import (
    CollectionMode,
    CommissionPolicyORM,
    CommissionReservationORM,
    DriverCollectionConfirmationORM,
    DriverTopupMethod,
    LedgerEntryType,
    PassengerPaymentMethod,
    PaymentIntentORM,
    PaymentIntentStatus,
    PaymentMethodORM,
    PaymentOutboxEventORM,
    PaymentStatus,
    ProviderStatus,
    ReservationStatus,
    RidePaymentORM,
    TopupORM,
    WalletLedgerEntryORM,
    WalletORM,
)


def _money(value: Any) -> float:
    return round(float(value or 0), 2)


def _wallet_snapshot(wallet: WalletORM) -> dict[str, float]:
    return {
        "available_balance": _money(wallet.available_balance),
        "reserved_balance": _money(wallet.reserved_balance),
        "current_balance": _money(wallet.current_balance),
    }


class PaymentRepository:
    def __init__(self, session: AsyncSession, event_topic: str = "payment-events") -> None:
        self._session = session
        self._event_topic = event_topic

    async def get_or_create_wallet(self, driver_id: UUID) -> WalletORM:
        result = await self._session.execute(select(WalletORM).where(WalletORM.driver_id == driver_id))
        wallet = result.scalar_one_or_none()
        if wallet:
            return wallet
        wallet = WalletORM(driver_id=driver_id)
        self._session.add(wallet)
        await self._session.flush()
        return wallet

    async def _locked_wallet(self, wallet_id: UUID) -> WalletORM:
        result = await self._session.execute(
            select(WalletORM).where(WalletORM.id == wallet_id).with_for_update()
        )
        wallet = result.scalar_one()
        return wallet

    async def list_ledger(self, wallet_id: UUID, *, limit: int = 50, offset: int = 0) -> list[WalletLedgerEntryORM]:
        result = await self._session.execute(
            select(WalletLedgerEntryORM)
            .where(WalletLedgerEntryORM.wallet_id == wallet_id)
            .order_by(WalletLedgerEntryORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def _add_ledger(
        self,
        wallet: WalletORM,
        entry_type: LedgerEntryType,
        amount: float,
        idempotency_key: str,
        *,
        before: dict,
        ride_id: UUID | None = None,
        reservation_id: UUID | None = None,
        topup_id: UUID | None = None,
        reason: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self._session.add(
            WalletLedgerEntryORM(
                wallet_id=wallet.id,
                driver_id=wallet.driver_id,
                ride_id=ride_id,
                reservation_id=reservation_id,
                topup_id=topup_id,
                entry_type=entry_type,
                amount=amount,
                currency=wallet.currency,
                balance_before=before,
                balance_after=_wallet_snapshot(wallet),
                source_service="payment",
                reason=reason,
                correlation_id=correlation_id,
                idempotency_key=idempotency_key,
            )
        )

    async def _outbox(
        self,
        event_type: str,
        aggregate_id: str,
        payload: dict,
        *,
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self._session.add(
            PaymentOutboxEventORM(
                event_type=event_type,
                aggregate_id=aggregate_id,
                aggregate_type="payment",
                topic=self._event_topic,
                payload=payload,
                idempotency_key=idempotency_key,
                correlation_id=correlation_id,
            )
        )

    async def get_active_policy(self, *, default_rate: float) -> CommissionPolicyORM:
        result = await self._session.execute(
            select(CommissionPolicyORM).where(CommissionPolicyORM.is_active.is_(True)).order_by(CommissionPolicyORM.effective_from.desc()).limit(1)
        )
        policy = result.scalar_one_or_none()
        if policy:
            return policy
        policy = CommissionPolicyORM(name="Default commission", rate=default_rate, currency="PKR")
        self._session.add(policy)
        await self._session.flush()
        return policy

    async def create_topup(self, wallet: WalletORM, req: CreateTopupRequest, idempotency_key: str) -> TopupORM:
        topup = TopupORM(wallet_id=wallet.id, driver_id=wallet.driver_id, method=DriverTopupMethod(req.method.value), amount=req.amount, currency=wallet.currency, status=ProviderStatus.PENDING)
        self._session.add(topup)
        await self._outbox("wallet.topup.initiated", str(topup.id), {"topup_id": str(topup.id), "driver_id": str(wallet.driver_id), "amount": req.amount}, idempotency_key=idempotency_key)
        await self._session.flush()
        return topup

    async def credit_topup(self, topup: TopupORM, idempotency_key: str) -> None:
        wallet = await self._locked_wallet(topup.wallet_id)
        before = _wallet_snapshot(wallet)
        wallet.available_balance = _money(wallet.available_balance) + _money(topup.amount)
        wallet.current_balance = _money(wallet.available_balance) + _money(wallet.reserved_balance)
        topup.status = ProviderStatus.SUCCEEDED
        await self._add_ledger(wallet, LedgerEntryType.TOPUP_CREDIT, _money(topup.amount), idempotency_key, before=before, topup_id=topup.id, reason="Sandbox topup credited")
        await self._outbox("wallet.topup.succeeded", str(topup.id), {"topup_id": str(topup.id), "driver_id": str(wallet.driver_id), "amount": _money(topup.amount)}, idempotency_key=f"{idempotency_key}:event")
        await self._session.flush()

    async def create_card(self, passenger_id: UUID, req: CreateSandboxCardRequest) -> PaymentMethodORM:
        if req.set_active:
            await self._session.execute(
                update(PaymentMethodORM)
                .where(PaymentMethodORM.owner_user_id == passenger_id, PaymentMethodORM.method_type == "CARD")
                .values(is_active=False)
            )
        method = PaymentMethodORM(
            owner_user_id=passenger_id,
            method_type="CARD",
            provider="SANDBOX",
            provider_payment_method_id=req.provider_payment_method_id,
            brand=req.brand,
            last4=req.last4,
            expiry_month=req.expiry_month,
            expiry_year=req.expiry_year,
            is_active=req.set_active,
        )
        self._session.add(method)
        await self._session.flush()
        return method

    async def list_payment_methods(self, passenger_id: UUID) -> list[PaymentMethodORM]:
        result = await self._session.execute(
            select(PaymentMethodORM).where(PaymentMethodORM.owner_user_id == passenger_id, PaymentMethodORM.is_deleted.is_(False))
        )
        return list(result.scalars().all())

    async def find_active_payment_method(self, passenger_id: UUID, method_id: UUID) -> PaymentMethodORM | None:
        result = await self._session.execute(
            select(PaymentMethodORM).where(
                PaymentMethodORM.id == method_id,
                PaymentMethodORM.owner_user_id == passenger_id,
                PaymentMethodORM.method_type == "CARD",
                PaymentMethodORM.is_active.is_(True),
                PaymentMethodORM.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def set_active_payment_method(self, passenger_id: UUID, method_id: UUID) -> PaymentMethodORM:
        await self._session.execute(
            update(PaymentMethodORM)
            .where(PaymentMethodORM.owner_user_id == passenger_id, PaymentMethodORM.method_type == "CARD")
            .values(is_active=False)
        )
        await self._session.execute(
            update(PaymentMethodORM)
            .where(PaymentMethodORM.id == method_id, PaymentMethodORM.owner_user_id == passenger_id)
            .values(is_active=True)
        )
        await self._session.flush()
        method = await self.find_active_payment_method(passenger_id, method_id)
        if method is None:
            raise ValueError("Payment method not found.")
        return method

    async def delete_payment_method(self, passenger_id: UUID, method_id: UUID) -> None:
        await self._session.execute(
            update(PaymentMethodORM)
            .where(PaymentMethodORM.id == method_id, PaymentMethodORM.owner_user_id == passenger_id)
            .values(is_deleted=True, is_active=False)
        )
        await self._session.flush()

    async def create_card_ride_payment(self, ride_id: UUID, req: CreateRidePaymentRequest, method: PaymentMethodORM, idempotency_key: str) -> RidePaymentORM:
        intent = PaymentIntentORM(
            ride_id=ride_id,
            passenger_id=req.passenger_id,
            amount_estimated=req.amount_estimated,
            currency=req.currency,
            status=PaymentIntentStatus.CREATED,
            active_payment_method_id=method.id,
            provider=method.provider,
        )
        self._session.add(intent)
        await self._session.flush()
        payment = RidePaymentORM(
            ride_id=ride_id,
            passenger_id=req.passenger_id,
            payment_intent_id=intent.id,
            passenger_payment_method=PassengerPaymentMethod.CARD,
            collection_mode=CollectionMode.PLATFORM_COLLECTED,
            amount_estimated=req.amount_estimated,
            status=PaymentStatus.PENDING,
            currency=req.currency,
        )
        self._session.add(payment)
        await self._outbox("payment.intent.created", str(intent.id), {"ride_id": str(ride_id), "payment_intent_id": str(intent.id)}, idempotency_key=idempotency_key, correlation_id=req.correlation_id)
        await self._session.flush()
        return payment

    async def create_driver_collected_ride_payment(self, ride_id: UUID, req: CreateRidePaymentRequest, idempotency_key: str) -> RidePaymentORM:
        payment = RidePaymentORM(
            ride_id=ride_id,
            passenger_id=req.passenger_id,
            passenger_payment_method=PassengerPaymentMethod(req.passenger_payment_method.value),
            collection_mode=CollectionMode.DRIVER_COLLECTED,
            amount_estimated=req.amount_estimated,
            status=PaymentStatus.PENDING,
            currency=req.currency,
        )
        self._session.add(payment)
        await self._session.flush()
        return payment

    async def find_ride_payment(self, ride_id: UUID) -> RidePaymentORM | None:
        result = await self._session.execute(select(RidePaymentORM).where(RidePaymentORM.ride_id == ride_id))
        return result.scalar_one_or_none()

    async def capture_payment_intent(self, ride_id: UUID, payment_intent_id: UUID, amount_final: float, idempotency_key: str) -> PaymentIntentORM:
        result = await self._session.execute(select(PaymentIntentORM).where(PaymentIntentORM.id == payment_intent_id, PaymentIntentORM.ride_id == ride_id))
        intent = result.scalar_one()
        intent.amount_final = amount_final
        intent.status = PaymentIntentStatus.CAPTURED
        await self._session.execute(
            update(RidePaymentORM)
            .where(RidePaymentORM.ride_id == ride_id)
            .values(amount_final=amount_final, status=PaymentStatus.PAID)
        )
        await self._outbox("payment.intent.captured", str(intent.id), {"ride_id": str(ride_id), "payment_intent_id": str(intent.id), "amount": amount_final}, idempotency_key=idempotency_key)
        await self._session.flush()
        return intent

    async def mark_driver_collected_unconfirmed(
        self,
        ride_id: UUID,
        driver_id: UUID,
        amount_final: float,
        idempotency_key: str,
        correlation_id: str | None,
    ) -> RidePaymentORM:
        result = await self._session.execute(select(RidePaymentORM).where(RidePaymentORM.ride_id == ride_id))
        payment = result.scalar_one()
        if payment.status != PaymentStatus.PAID:
            payment.amount_final = amount_final
            payment.status = PaymentStatus.COLLECTION_UNCONFIRMED
            await self._outbox(
                "driver.collection.unconfirmed",
                str(payment.id),
                {"ride_id": str(ride_id), "driver_id": str(driver_id), "amount": amount_final},
                idempotency_key=idempotency_key,
                correlation_id=correlation_id,
            )
        await self._session.flush()
        return payment

    async def reserve_commission(
        self,
        ride_id: UUID,
        driver_id: UUID,
        wallet: WalletORM,
        policy: CommissionPolicyORM,
        basis_amount: float,
        commission: float,
        currency: str,
        expires_at: datetime,
        idempotency_key: str,
        correlation_id: str | None,
    ) -> CommissionReservationORM:
        wallet = await self._locked_wallet(wallet.id)
        before = _wallet_snapshot(wallet)
        wallet.available_balance = _money(wallet.available_balance) - commission
        wallet.reserved_balance = _money(wallet.reserved_balance) + commission
        wallet.current_balance = _money(wallet.available_balance) + _money(wallet.reserved_balance)
        reservation = CommissionReservationORM(
            ride_id=ride_id,
            driver_id=driver_id,
            wallet_id=wallet.id,
            commission_policy_id=policy.id,
            rate_snapshot=policy.rate,
            basis_amount=basis_amount,
            reserved_amount=commission,
            currency=currency,
            calculation_details={"basis_amount": basis_amount, "rate": float(policy.rate)},
            expires_at=expires_at,
        )
        self._session.add(reservation)
        await self._session.flush()
        await self._add_ledger(wallet, LedgerEntryType.COMMISSION_RESERVE, commission, idempotency_key, before=before, ride_id=ride_id, reservation_id=reservation.id, reason="Commission reserved", correlation_id=correlation_id)
        await self._outbox("commission.reserved", str(reservation.id), {"ride_id": str(ride_id), "driver_id": str(driver_id), "reservation_id": str(reservation.id), "amount": commission, "currency": currency}, idempotency_key=f"{idempotency_key}:event", correlation_id=correlation_id)
        await self._session.flush()
        return reservation

    async def find_active_reservation(self, ride_id: UUID, driver_id: UUID | None = None) -> CommissionReservationORM | None:
        stmt = select(CommissionReservationORM).where(CommissionReservationORM.ride_id == ride_id, CommissionReservationORM.status == ReservationStatus.RESERVED)
        if driver_id:
            stmt = stmt.where(CommissionReservationORM.driver_id == driver_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def capture_commission(self, reservation: CommissionReservationORM, final_amount: float, actual_commission: float, idempotency_key: str, correlation_id: str | None) -> CommissionReservationORM:
        wallet = await self._locked_wallet(reservation.wallet_id)
        delta = round(actual_commission - _money(reservation.reserved_amount), 2)
        if delta > 0:
            before = _wallet_snapshot(wallet)
            wallet.available_balance = _money(wallet.available_balance) - delta
            wallet.current_balance = _money(wallet.available_balance) + _money(wallet.reserved_balance)
            await self._add_ledger(wallet, LedgerEntryType.COMMISSION_DELTA_DEBIT, delta, f"{idempotency_key}:delta", before=before, ride_id=reservation.ride_id, reservation_id=reservation.id, reason="Final commission exceeded reservation", correlation_id=correlation_id)
        elif delta < 0:
            release = abs(delta)
            before = _wallet_snapshot(wallet)
            wallet.reserved_balance = _money(wallet.reserved_balance) - release
            wallet.available_balance = _money(wallet.available_balance) + release
            wallet.current_balance = _money(wallet.available_balance) + _money(wallet.reserved_balance)
            await self._add_ledger(wallet, LedgerEntryType.COMMISSION_DELTA_RELEASE, release, f"{idempotency_key}:delta", before=before, ride_id=reservation.ride_id, reservation_id=reservation.id, reason="Final commission below reservation", correlation_id=correlation_id)
        before = _wallet_snapshot(wallet)
        capture_amount = actual_commission
        wallet.reserved_balance = _money(wallet.reserved_balance) - min(_money(reservation.reserved_amount), capture_amount)
        wallet.current_balance = _money(wallet.available_balance) + _money(wallet.reserved_balance)
        reservation.basis_amount = final_amount
        reservation.captured_amount = capture_amount
        reservation.released_amount = max(0.0, _money(reservation.reserved_amount) - capture_amount)
        reservation.status = ReservationStatus.CAPTURED
        await self._add_ledger(wallet, LedgerEntryType.COMMISSION_CAPTURE, capture_amount, idempotency_key, before=before, ride_id=reservation.ride_id, reservation_id=reservation.id, reason="Commission captured", correlation_id=correlation_id)
        await self._outbox("commission.captured", str(reservation.id), {"ride_id": str(reservation.ride_id), "driver_id": str(reservation.driver_id), "reservation_id": str(reservation.id), "amount": capture_amount}, idempotency_key=f"{idempotency_key}:event", correlation_id=correlation_id)
        await self._session.flush()
        return reservation

    async def release_commission(self, reservation: CommissionReservationORM, idempotency_key: str, correlation_id: str | None, reason: str | None) -> CommissionReservationORM:
        wallet = await self._locked_wallet(reservation.wallet_id)
        amount = _money(reservation.reserved_amount) - _money(reservation.captured_amount) - _money(reservation.released_amount)
        before = _wallet_snapshot(wallet)
        wallet.reserved_balance = _money(wallet.reserved_balance) - amount
        wallet.available_balance = _money(wallet.available_balance) + amount
        wallet.current_balance = _money(wallet.available_balance) + _money(wallet.reserved_balance)
        reservation.released_amount = _money(reservation.released_amount) + amount
        reservation.status = ReservationStatus.RELEASED
        await self._add_ledger(wallet, LedgerEntryType.COMMISSION_RELEASE, amount, idempotency_key, before=before, ride_id=reservation.ride_id, reservation_id=reservation.id, reason=reason or "Commission released", correlation_id=correlation_id)
        await self._outbox("commission.released", str(reservation.id), {"ride_id": str(reservation.ride_id), "driver_id": str(reservation.driver_id), "reservation_id": str(reservation.id), "amount": amount}, idempotency_key=f"{idempotency_key}:event", correlation_id=correlation_id)
        await self._session.flush()
        return reservation

    async def expire_stale_reservations(self) -> int:
        result = await self._session.execute(
            select(CommissionReservationORM).where(
                CommissionReservationORM.status == ReservationStatus.RESERVED,
                CommissionReservationORM.expires_at <= datetime.now(timezone.utc),
            )
        )
        reservations = list(result.scalars().all())
        for reservation in reservations:
            await self.release_commission(reservation, f"expire:{reservation.id}", None, "Reservation expired")
            reservation.status = ReservationStatus.EXPIRED
            await self._outbox("commission.expired", str(reservation.id), {"ride_id": str(reservation.ride_id), "reservation_id": str(reservation.id)}, idempotency_key=f"expire:{reservation.id}:event")
        return len(reservations)

    async def confirm_driver_collection(self, ride_id: UUID, req: CollectionConfirmationRequest, idempotency_key: str) -> DriverCollectionConfirmationORM:
        confirmation = DriverCollectionConfirmationORM(
            ride_id=ride_id,
            driver_id=req.driver_id,
            passenger_id=req.passenger_id,
            method=PassengerPaymentMethod(req.method.value),
            amount_collected=req.amount_collected,
            notes=req.notes,
        )
        self._session.add(confirmation)
        await self._session.execute(
            update(RidePaymentORM)
            .where(RidePaymentORM.ride_id == ride_id)
            .values(amount_final=req.amount_collected, status=PaymentStatus.PAID)
        )
        await self._outbox("driver.collection.confirmed", str(confirmation.id), {"ride_id": str(ride_id), "driver_id": str(req.driver_id), "amount": req.amount_collected}, idempotency_key=idempotency_key)
        await self._session.flush()
        return confirmation
