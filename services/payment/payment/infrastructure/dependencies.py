from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.core.config import Settings
from sp.infrastructure.db.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    CommissionUseCases,
    DriverEarningsUseCases,
    PaymentMethodUseCases,
    RidePaymentUseCases,
    WalletUseCases,
)
from .repositories import PaymentRepository


def get_settings_from_app(request: Request) -> Settings:
    return request.app.state.settings


def get_payment_repo(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PaymentRepository:
    topic = getattr(request.app.state.settings, "PAYMENT_EVENTS_TOPIC", "payment-events")
    return PaymentRepository(session, event_topic=topic)


def get_wallet_uc(
    repo: Annotated[PaymentRepository, Depends(get_payment_repo)],
    settings: Annotated[Settings, Depends(get_settings_from_app)],
) -> WalletUseCases:
    return WalletUseCases(repo, settings)


def get_payment_method_uc(repo: Annotated[PaymentRepository, Depends(get_payment_repo)]) -> PaymentMethodUseCases:
    return PaymentMethodUseCases(repo)


def get_ride_payment_uc(repo: Annotated[PaymentRepository, Depends(get_payment_repo)]) -> RidePaymentUseCases:
    return RidePaymentUseCases(repo)


def get_commission_uc(
    repo: Annotated[PaymentRepository, Depends(get_payment_repo)],
    settings: Annotated[Settings, Depends(get_settings_from_app)],
) -> CommissionUseCases:
    return CommissionUseCases(repo, settings)


def get_driver_earnings_uc(repo: Annotated[PaymentRepository, Depends(get_payment_repo)]) -> DriverEarningsUseCases:
    return DriverEarningsUseCases(repo)
