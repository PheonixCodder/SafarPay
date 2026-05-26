from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.schemas import (
    CollectionConfirmationRequest,
    CreateRidePaymentRequest,
    CreateSandboxCardRequest,
    CreateTopupRequest,
    DriverEarningsBreakdownItem,
    DriverEarningsResponse,
    DriverEarningsSummary,
    DriverEarningsTrip,
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


def _period_bounds(period: str) -> tuple[datetime, datetime, list[date]]:
    now = datetime.now(timezone.utc)
    today = now.date()
    if period == "today":
        start_day = today
    elif period == "month":
        start_day = today.replace(day=1)
    else:
        start_day = today - timedelta(days=6)

    start = datetime.combine(start_day, time.min, tzinfo=timezone.utc)
    days = [start_day + timedelta(days=offset) for offset in range((today - start_day).days + 1)]
    return start, now, days


def _date_label(value: date) -> str:
    return value.strftime("%a")


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

    async def get_driver_earnings(self, driver_id: UUID, period: str) -> DriverEarningsResponse:
        start, end, days = _period_bounds(period)
        wallet = await self.get_or_create_wallet(driver_id)
        stats = await self._driver_stats(driver_id)
        trips = await self._driver_completed_trip_rows(driver_id, start, end)

        gross_fares = _money(sum(float(row["final_fare"] or 0) for row in trips))
        commission_total = _money(sum(float(row["commission"] or 0) for row in trips))
        cash_collected = _money(
            sum(
                float(row["final_fare"] or 0)
                for row in trips
                if (row["collection_mode"] or "") == CollectionMode.DRIVER_COLLECTED.value
            )
        )
        platform_collected = _money(
            sum(
                float(row["final_fare"] or 0)
                for row in trips
                if (row["collection_mode"] or "") == CollectionMode.PLATFORM_COLLECTED.value
            )
        )
        active_minutes = sum(int(row["active_minutes"] or 0) for row in trips)

        by_day: dict[date, dict[str, float | int]] = {
            day: {
                "gross_fares": 0.0,
                "commission_total": 0.0,
                "net_earnings": 0.0,
                "completed_trips": 0,
            }
            for day in days
        }
        for row in trips:
            completed_at = row["completed_at"]
            completed_day = completed_at.date()
            if completed_day not in by_day:
                continue
            final_fare = _money(row["final_fare"])
            commission = _money(row["commission"])
            by_day[completed_day]["gross_fares"] = _money(by_day[completed_day]["gross_fares"] + final_fare)
            by_day[completed_day]["commission_total"] = _money(by_day[completed_day]["commission_total"] + commission)
            by_day[completed_day]["net_earnings"] = _money(by_day[completed_day]["net_earnings"] + final_fare - commission)
            by_day[completed_day]["completed_trips"] = int(by_day[completed_day]["completed_trips"]) + 1

        return DriverEarningsResponse(
            period=period,  # type: ignore[arg-type]
            currency=wallet.currency,
            summary=DriverEarningsSummary(
                net_earnings=_money(gross_fares - commission_total),
                gross_fares=gross_fares,
                commission_total=commission_total,
                available_balance=_money(wallet.available_balance),
                reserved_balance=_money(wallet.reserved_balance),
                completed_trips=len(trips),
                active_minutes=active_minutes,
                rating_avg=stats["rating_avg"],
                cash_collected=cash_collected,
                platform_collected=platform_collected,
            ),
            daily_breakdown=[
                DriverEarningsBreakdownItem(
                    label=_date_label(day),
                    date=day.isoformat(),
                    gross_fares=_money(values["gross_fares"]),
                    commission_total=_money(values["commission_total"]),
                    net_earnings=_money(values["net_earnings"]),
                    completed_trips=int(values["completed_trips"]),
                )
                for day, values in by_day.items()
            ],
            recent_trips=[
                DriverEarningsTrip(
                    ride_id=row["ride_id"],
                    completed_at=row["completed_at"],
                    pickup_label=row["pickup_label"] or "Pickup",
                    dropoff_label=row["dropoff_label"] or "Dropoff",
                    service_type=row["service_type"] or "CITY_RIDE",
                    final_fare=_money(row["final_fare"]),
                    commission=_money(row["commission"]),
                    net_earning=_money(_money(row["final_fare"]) - _money(row["commission"])),
                    collection_mode=row["collection_mode"] or CollectionMode.DRIVER_COLLECTED.value,
                )
                for row in trips[:10]
            ],
            withdraw_available=False,
            withdraw_unavailable_reason="Withdrawals are not enabled yet.",
        )

    async def _driver_stats(self, driver_id: UUID) -> dict[str, float | None]:
        result = await self._session.execute(
            text(
                """
                SELECT rating_avg
                FROM verification.driver_stats
                WHERE driver_id = :driver_id
                LIMIT 1
                """
            ),
            {"driver_id": driver_id},
        )
        row = result.mappings().first()
        return {"rating_avg": _money(row["rating_avg"]) if row and row["rating_avg"] is not None else None}

    async def _driver_completed_trip_rows(self, driver_id: UUID, start: datetime, end: datetime) -> list[dict[str, Any]]:
        result = await self._session.execute(
            text(
                """
                WITH commission_by_ride AS (
                    SELECT
                        ride_id,
                        driver_id,
                        SUM(COALESCE(captured_amount, 0)) AS commission
                    FROM payment.commission_reservations
                    WHERE driver_id = :driver_id
                    GROUP BY ride_id, driver_id
                ),
                first_pickup AS (
                    SELECT DISTINCT ON (service_request_id)
                        service_request_id,
                        COALESCE(place_name, address_line_1, city, 'Pickup') AS pickup_label
                    FROM service_request.service_stops
                    WHERE stop_type = 'PICKUP'
                    ORDER BY service_request_id, sequence_order ASC
                ),
                last_dropoff AS (
                    SELECT DISTINCT ON (service_request_id)
                        service_request_id,
                        COALESCE(place_name, address_line_1, city, 'Dropoff') AS dropoff_label
                    FROM service_request.service_stops
                    WHERE stop_type = 'DROPOFF'
                    ORDER BY service_request_id, sequence_order DESC
                )
                SELECT
                    sr.id AS ride_id,
                    COALESCE(sr.completed_at, sr.updated_at, sr.created_at) AS completed_at,
                    fp.pickup_label,
                    ld.dropoff_label,
                    sr.service_type::text AS service_type,
                    COALESCE(rp.amount_final, sr.final_price, ba.final_price, 0) AS final_fare,
                    COALESCE(cbr.commission, 0) AS commission,
                    COALESCE(rp.collection_mode::text, sr.payment_collection_mode, 'DRIVER_COLLECTED') AS collection_mode,
                    GREATEST(
                        0,
                        FLOOR(EXTRACT(EPOCH FROM (COALESCE(sr.completed_at, sr.updated_at, sr.created_at) - COALESCE(sr.accepted_at, sr.created_at))) / 60)
                    )::int AS active_minutes
                FROM service_request.service_requests sr
                LEFT JOIN payment.ride_payments rp ON rp.ride_id = sr.id
                LEFT JOIN commission_by_ride cbr ON cbr.ride_id = sr.id AND cbr.driver_id = sr.assigned_driver_id
                LEFT JOIN bidding.bid_acceptances ba ON ba.service_request_id = sr.id
                LEFT JOIN first_pickup fp ON fp.service_request_id = sr.id
                LEFT JOIN last_dropoff ld ON ld.service_request_id = sr.id
                WHERE sr.assigned_driver_id = :driver_id
                  AND sr.status = 'COMPLETED'
                  AND COALESCE(sr.completed_at, sr.updated_at, sr.created_at) >= :start
                  AND COALESCE(sr.completed_at, sr.updated_at, sr.created_at) <= :end
                ORDER BY completed_at DESC
                """
            ),
            {"driver_id": driver_id, "start": start, "end": end},
        )
        return [dict(row) for row in result.mappings().all()]

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
