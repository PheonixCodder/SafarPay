from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sp.infrastructure.security.dependencies import CurrentDriver, CurrentUser

from ..application.schemas import (
    CaptureCommissionRequest,
    CapturePaymentIntentRequest,
    CollectionConfirmationRequest,
    CollectionConfirmationResponse,
    CompleteRidePaymentRequest,
    CreateRidePaymentRequest,
    CreateSandboxCardRequest,
    CreateTopupRequest,
    EligibilityRequest,
    EligibilityResponse,
    LedgerEntryResponse,
    PaymentIntentResponse,
    PaymentMethodResponse,
    ReleaseCommissionRequest,
    ReservationResponse,
    ReserveCommissionRequest,
    RidePaymentResponse,
    SetupIntentResponse,
    TopupResponse,
    WalletResponse,
)
from ..application.use_cases import (
    CommissionUseCases,
    PaymentMethodUseCases,
    RidePaymentUseCases,
    WalletUseCases,
)
from ..domain.exceptions import (
    InsufficientWalletBalanceError,
    ReservationNotFoundError,
    WalletFrozenError,
)
from ..infrastructure.dependencies import (
    get_commission_uc,
    get_payment_method_uc,
    get_ride_payment_uc,
    get_wallet_uc,
)

router = APIRouter(tags=["payments"])


def _idem(value: str | None) -> str:
    if not value:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required.")
    return value


def _wallet_response(wallet) -> WalletResponse:
    return WalletResponse(
        id=wallet.id,
        driver_id=wallet.driver_id,
        available_balance=float(wallet.available_balance),
        reserved_balance=float(wallet.reserved_balance),
        current_balance=float(wallet.current_balance),
        currency=wallet.currency,
        status=wallet.status.value,
        negative_limit=float(wallet.negative_limit),
        max_reserved_limit=float(wallet.max_reserved_limit),
    )


def _reservation_response(reservation) -> ReservationResponse:
    return ReservationResponse(
        id=reservation.id,
        ride_id=reservation.ride_id,
        driver_id=reservation.driver_id,
        wallet_id=reservation.wallet_id,
        basis_amount=float(reservation.basis_amount),
        reserved_amount=float(reservation.reserved_amount),
        captured_amount=float(reservation.captured_amount),
        released_amount=float(reservation.released_amount),
        currency=reservation.currency,
        status=reservation.status.value,
        expires_at=reservation.expires_at,
    )


def _ride_payment_response(payment) -> RidePaymentResponse:
    return RidePaymentResponse(
        id=payment.id,
        ride_id=payment.ride_id,
        passenger_id=payment.passenger_id,
        payment_intent_id=payment.payment_intent_id,
        passenger_payment_method=payment.passenger_payment_method.value,
        collection_mode=payment.collection_mode.value,
        amount_estimated=float(payment.amount_estimated) if payment.amount_estimated is not None else None,
        amount_final=float(payment.amount_final) if payment.amount_final is not None else None,
        status=payment.status.value,
        currency=payment.currency,
    )


@router.get("/wallets/me", response_model=WalletResponse)
async def get_wallet(driver_id: CurrentDriver, uc: Annotated[WalletUseCases, Depends(get_wallet_uc)]) -> WalletResponse:
    return _wallet_response(await uc.get_or_create_wallet(driver_id))


@router.get("/wallets/me/ledger", response_model=list[LedgerEntryResponse])
async def get_ledger(
    driver_id: CurrentDriver,
    uc: Annotated[WalletUseCases, Depends(get_wallet_uc)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[LedgerEntryResponse]:
    entries = await uc.get_ledger(driver_id, limit=limit, offset=offset)
    return [
        LedgerEntryResponse(
            id=e.id,
            wallet_id=e.wallet_id,
            driver_id=e.driver_id,
            ride_id=e.ride_id,
            entry_type=e.entry_type.value,
            amount=float(e.amount),
            currency=e.currency,
            created_at=e.created_at,
            reason=e.reason,
        )
        for e in entries
    ]


@router.post("/wallets/topups", response_model=TopupResponse, status_code=status.HTTP_201_CREATED)
async def create_topup(
    body: CreateTopupRequest,
    driver_id: CurrentDriver,
    uc: Annotated[WalletUseCases, Depends(get_wallet_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> TopupResponse:
    topup = await uc.create_topup(driver_id, body, _idem(idempotency_key))
    return TopupResponse(
        id=topup.id,
        wallet_id=topup.wallet_id,
        driver_id=topup.driver_id,
        method=topup.method.value,
        amount=float(topup.amount),
        currency=topup.currency,
        status=topup.status.value,
    )


@router.post("/payment-methods/cards/setup-intent", response_model=SetupIntentResponse)
async def setup_card(current_user: CurrentUser, uc: Annotated[PaymentMethodUseCases, Depends(get_payment_method_uc)]) -> SetupIntentResponse:
    return SetupIntentResponse(**await uc.setup_intent(current_user.user_id))


@router.post("/payment-methods/cards/sandbox", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_sandbox_card(
    body: CreateSandboxCardRequest,
    current_user: CurrentUser,
    uc: Annotated[PaymentMethodUseCases, Depends(get_payment_method_uc)],
) -> PaymentMethodResponse:
    method = await uc.create_sandbox_card(current_user.user_id, body)
    return PaymentMethodResponse(
        id=method.id,
        method_type=method.method_type,
        provider=method.provider,
        brand=method.brand,
        last4=method.last4,
        expiry_month=method.expiry_month,
        expiry_year=method.expiry_year,
        is_active=method.is_active,
    )


@router.get("/payment-methods", response_model=list[PaymentMethodResponse])
async def list_payment_methods(current_user: CurrentUser, uc: Annotated[PaymentMethodUseCases, Depends(get_payment_method_uc)]) -> list[PaymentMethodResponse]:
    methods = await uc.list_methods(current_user.user_id)
    return [
        PaymentMethodResponse(
            id=m.id,
            method_type=m.method_type,
            provider=m.provider,
            brand=m.brand,
            last4=m.last4,
            expiry_month=m.expiry_month,
            expiry_year=m.expiry_year,
            is_active=m.is_active,
        )
        for m in methods
    ]


@router.post("/payment-methods/{method_id}/set-active", response_model=PaymentMethodResponse)
async def set_active_method(method_id: UUID, current_user: CurrentUser, uc: Annotated[PaymentMethodUseCases, Depends(get_payment_method_uc)]) -> PaymentMethodResponse:
    method = await uc.set_active(current_user.user_id, method_id)
    return PaymentMethodResponse(
        id=method.id,
        method_type=method.method_type,
        provider=method.provider,
        brand=method.brand,
        last4=method.last4,
        expiry_month=method.expiry_month,
        expiry_year=method.expiry_year,
        is_active=method.is_active,
    )


@router.delete("/payment-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_method(method_id: UUID, current_user: CurrentUser, uc: Annotated[PaymentMethodUseCases, Depends(get_payment_method_uc)]) -> None:
    await uc.delete(current_user.user_id, method_id)


@router.get("/rides/{ride_id}/payment", response_model=RidePaymentResponse)
async def get_ride_payment(ride_id: UUID, uc: Annotated[RidePaymentUseCases, Depends(get_ride_payment_uc)]) -> RidePaymentResponse:
    payment = await uc.get_ride_payment(ride_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Ride payment not found.")
    return _ride_payment_response(payment)


@router.post("/rides/{ride_id}/collection-confirmations", response_model=CollectionConfirmationResponse, status_code=status.HTTP_201_CREATED)
async def confirm_collection(
    ride_id: UUID,
    body: CollectionConfirmationRequest,
    driver_id: CurrentDriver,
    uc: Annotated[RidePaymentUseCases, Depends(get_ride_payment_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> CollectionConfirmationResponse:
    if body.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Driver can only confirm their own collection.")
    c = await uc.confirm_collection(ride_id, body, _idem(idempotency_key))
    return CollectionConfirmationResponse(
        id=c.id,
        ride_id=c.ride_id,
        driver_id=c.driver_id,
        passenger_id=c.passenger_id,
        method=c.method.value,
        amount_collected=float(c.amount_collected),
        confirmed_by_driver_at=c.confirmed_by_driver_at,
        confirmed_by_passenger_at=c.confirmed_by_passenger_at,
        is_disputed=c.is_disputed,
    )


@router.post("/internal/rides/{ride_id}/payments", response_model=RidePaymentResponse)
async def internal_create_ride_payment(
    ride_id: UUID,
    body: CreateRidePaymentRequest,
    uc: Annotated[RidePaymentUseCases, Depends(get_ride_payment_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> RidePaymentResponse:
    payment = await uc.create_ride_payment(ride_id, body, _idem(idempotency_key))
    return _ride_payment_response(payment)


@router.post("/internal/rides/{ride_id}/payment-intents/{payment_intent_id}/capture", response_model=PaymentIntentResponse)
async def internal_capture_payment_intent(
    ride_id: UUID,
    payment_intent_id: UUID,
    body: CapturePaymentIntentRequest,
    uc: Annotated[RidePaymentUseCases, Depends(get_ride_payment_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> PaymentIntentResponse:
    intent = await uc.capture_payment_intent(ride_id, payment_intent_id, body.amount_final, _idem(idempotency_key))
    return PaymentIntentResponse(
        id=intent.id,
        ride_id=intent.ride_id,
        passenger_id=intent.passenger_id,
        amount_estimated=float(intent.amount_estimated) if intent.amount_estimated is not None else None,
        amount_final=float(intent.amount_final) if intent.amount_final is not None else None,
        currency=intent.currency,
        status=intent.status.value,
        active_payment_method_id=intent.active_payment_method_id,
        provider=intent.provider,
    )


@router.post("/internal/rides/{ride_id}/payments/complete", response_model=RidePaymentResponse)
async def internal_complete_ride_payment(
    ride_id: UUID,
    body: CompleteRidePaymentRequest,
    uc: Annotated[RidePaymentUseCases, Depends(get_ride_payment_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> RidePaymentResponse:
    try:
        payment = await uc.complete_ride_payment(ride_id, body, _idem(idempotency_key))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return _ride_payment_response(payment)


@router.post("/internal/rides/{ride_id}/commission/reserve", response_model=ReservationResponse)
async def internal_reserve_commission(
    ride_id: UUID,
    body: ReserveCommissionRequest,
    uc: Annotated[CommissionUseCases, Depends(get_commission_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ReservationResponse:
    try:
        return _reservation_response(await uc.reserve(ride_id, body, _idem(idempotency_key)))
    except (WalletFrozenError, InsufficientWalletBalanceError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@router.post("/internal/rides/{ride_id}/commission/capture", response_model=ReservationResponse)
async def internal_capture_commission(
    ride_id: UUID,
    body: CaptureCommissionRequest,
    uc: Annotated[CommissionUseCases, Depends(get_commission_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ReservationResponse:
    try:
        return _reservation_response(await uc.capture(ride_id, body, _idem(idempotency_key)))
    except ReservationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.post("/internal/rides/{ride_id}/commission/release", response_model=ReservationResponse | None)
async def internal_release_commission(
    ride_id: UUID,
    body: ReleaseCommissionRequest,
    uc: Annotated[CommissionUseCases, Depends(get_commission_uc)],
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ReservationResponse | None:
    reservation = await uc.release(ride_id, body, _idem(idempotency_key))
    return _reservation_response(reservation) if reservation else None


@router.post("/internal/drivers/{driver_id}/eligibility/ride", response_model=EligibilityResponse)
async def internal_driver_eligibility(
    driver_id: UUID,
    body: EligibilityRequest,
    uc: Annotated[CommissionUseCases, Depends(get_commission_uc)],
) -> EligibilityResponse:
    eligible, reason, wallet, required = await uc.check_eligibility(driver_id, body)
    return EligibilityResponse(
        eligible=eligible,
        reason=reason,
        wallet_id=wallet.id if wallet else None,
        required_commission=required,
        available_balance=float(wallet.available_balance) if wallet else None,
        reserved_balance=float(wallet.reserved_balance) if wallet else None,
    )


@router.post("/internal/commission/expire-stale", response_model=dict)
async def internal_expire_stale(uc: Annotated[CommissionUseCases, Depends(get_commission_uc)]) -> dict:
    return {"expired": await uc.expire_stale()}
