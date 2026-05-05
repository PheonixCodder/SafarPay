"""FastAPI dependencies for the verification service."""
from typing import Annotated

from fastapi import Depends, Request
from sp.core.config import get_settings
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.security.dependencies import get_current_user
from sp.infrastructure.security.jwt import TokenPayload
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.services.identity_verification_engine import IdentityVerificationEngine
from ..application.services.rejection_resolver import RejectionResolver
from ..domain.interfaces import (
    DocumentRepositoryProtocol,
    DriverRepositoryProtocol,
    DriverVehicleRepositoryProtocol,
    StorageProviderProtocol,
    VehicleRepositoryProtocol,
    VerificationRejectionRepositoryProtocol,
)
from .outbox_publisher import VerificationOutboxPublisher
from .repositories import (
    DocumentRepository,
    DriverRepository,
    DriverVehicleRepository,
    VehicleRepository,
    VerificationRejectionRepository,
)
from .storage import S3StorageProvider

# ── Type Aliases ─────────────────────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


# ── Repositories ─────────────────────────────────────────────────────────────
def get_driver_repository(session: DBSession) -> DriverRepositoryProtocol:
    return DriverRepository(session)


def get_vehicle_repository(session: DBSession) -> VehicleRepositoryProtocol:
    return VehicleRepository(session)


def get_document_repository(session: DBSession) -> DocumentRepositoryProtocol:
    return DocumentRepository(session)


def get_driver_vehicle_repository(
    session: DBSession,
) -> DriverVehicleRepositoryProtocol:
    return DriverVehicleRepository(session)


def get_verification_rejection_repository(
    session: DBSession,
) -> VerificationRejectionRepositoryProtocol:
    return VerificationRejectionRepository(session)


# ── Providers & Services ─────────────────────────────────────────────────────
def get_storage_provider() -> StorageProviderProtocol:
    return S3StorageProvider()


def get_rejection_resolver(
    rejection_repo: Annotated[VerificationRejectionRepositoryProtocol, Depends(get_verification_rejection_repository)]
) -> RejectionResolver:
    return RejectionResolver(rejection_repo)


def get_identity_engine(request: Request) -> IdentityVerificationEngine:
    return request.app.state.identity_engine


def get_event_publisher(request: Request, session: DBSession) -> VerificationOutboxPublisher | EventPublisher:
    if getattr(request.app.state, "outbox_worker", None):
        return VerificationOutboxPublisher(session)
    settings = get_settings()
    return getattr(request.app.state, "publisher", EventPublisher(settings.VERIFICATION_EVENTS_TOPIC))


def get_cache_manager(request: Request) -> CacheManager:
    return request.app.state.cache


# ── Dependency Types ─────────────────────────────────────────────────────────
DriverRepo = Annotated[DriverRepositoryProtocol, Depends(get_driver_repository)]
VehicleRepo = Annotated[VehicleRepositoryProtocol, Depends(get_vehicle_repository)]
DocumentRepo = Annotated[DocumentRepositoryProtocol, Depends(get_document_repository)]
DriverVehicleRepo = Annotated[
    DriverVehicleRepositoryProtocol, Depends(get_driver_vehicle_repository)
]
VerificationRejectionRepo = Annotated[
    VerificationRejectionRepositoryProtocol, Depends(get_verification_rejection_repository)
]
StorageProvider = Annotated[StorageProviderProtocol, Depends(get_storage_provider)]
Resolver = Annotated[RejectionResolver, Depends(get_rejection_resolver)]
IdentityEngine = Annotated[IdentityVerificationEngine, Depends(get_identity_engine)]
EventPub = Annotated[EventPublisher, Depends(get_event_publisher)]
Cache = Annotated[CacheManager, Depends(get_cache_manager)]
