"""Ride service DI providers — wire every use case from app.state."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.messaging.publisher import EventPublisher
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    AcceptRideUseCase,
    AddStopUseCase,
    BroadcastRideToDriversUseCase,
    CancelRideUseCase,
    CompleteRideUseCase,
    FindNearbyDriversUseCase,
    GenerateProofUploadUrlUseCase,
    GenerateVerificationCodeUseCase,
    GetProofWithUrlUseCase,
    GetRideUseCase,
    ListPassengerRidesUseCase,
    MarkStopArrivedUseCase,
    MarkStopCompletedUseCase,
    StartRideUseCase,
    UploadProofUseCase,
    VerifyVerificationCodeUseCase,
    CreateRideUseCase,
)
from .storage import S3StorageProvider
from ..domain.interfaces import (
    GeospatialClientProtocol,
    ProofImageRepositoryProtocol,
    ServiceRequestRepositoryProtocol,
    StopRepositoryProtocol,
    VerificationCodeRepositoryProtocol,
    WebhookClientProtocol,
)
from .repositories import (
    ProofImageRepository,
    ServiceRequestRepository,
    StopRepository,
    VerificationCodeRepository,
)
from .websocket_manager import WebSocketManager


# ---------------------------------------------------------------------------
# Raw infrastructure providers
# ---------------------------------------------------------------------------

def get_cache(request: Request) -> CacheManager:
    return request.app.state.cache


def get_publisher(request: Request) -> EventPublisher | None:
    return getattr(request.app.state, "publisher", None)


def get_ws_manager(request: Request) -> WebSocketManager:
    return request.app.state.ws_manager


def get_webhook(request: Request) -> WebhookClientProtocol:
    return request.app.state.webhook_client


def get_geo(request: Request) -> GeospatialClientProtocol:
    return request.app.state.geo_client


def get_storage(request: Request) -> S3StorageProvider:
    """Return the S3StorageProvider stored on app.state at lifespan."""
    return request.app.state.storage


# ---------------------------------------------------------------------------
# Repository providers
# ---------------------------------------------------------------------------

def get_ride_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ServiceRequestRepositoryProtocol:
    return ServiceRequestRepository(session)


def get_stop_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StopRepositoryProtocol:
    return StopRepository(session)


def get_proof_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ProofImageRepositoryProtocol:
    return ProofImageRepository(session)


def get_code_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> VerificationCodeRepositoryProtocol:
    return VerificationCodeRepository(session)


# ---------------------------------------------------------------------------
# Use case providers
# ---------------------------------------------------------------------------

def get_create_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> CreateRideUseCase:
    return CreateRideUseCase(repo=repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_get_ride_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], request: Request) -> GetRideUseCase:
    return GetRideUseCase(repo=repo, cache=get_cache(request))


def get_list_rides_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> ListPassengerRidesUseCase:
    return ListPassengerRidesUseCase(repo=repo)


def get_cancel_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> CancelRideUseCase:
    return CancelRideUseCase(repo=repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_accept_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)]) -> AcceptRideUseCase:
    return AcceptRideUseCase(repo=repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_start_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)]) -> StartRideUseCase:
    return StartRideUseCase(repo=repo, code_repo=code_repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_complete_ride_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)]) -> CompleteRideUseCase:
    return CompleteRideUseCase(repo=repo, code_repo=code_repo, cache=get_cache(request), ws=get_ws_manager(request), publisher=get_publisher(request))


def get_add_stop_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], stop_repo: Annotated[StopRepositoryProtocol, Depends(get_stop_repo)]) -> AddStopUseCase:
    return AddStopUseCase(repo=repo, stop_repo=stop_repo, ws=get_ws_manager(request), publisher=get_publisher(request))


def get_mark_arrived_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], stop_repo: Annotated[StopRepositoryProtocol, Depends(get_stop_repo)]) -> MarkStopArrivedUseCase:
    return MarkStopArrivedUseCase(repo=repo, stop_repo=stop_repo, ws=get_ws_manager(request), publisher=get_publisher(request))


def get_mark_completed_uc(request: Request, repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], stop_repo: Annotated[StopRepositoryProtocol, Depends(get_stop_repo)]) -> MarkStopCompletedUseCase:
    return MarkStopCompletedUseCase(repo=repo, stop_repo=stop_repo, ws=get_ws_manager(request), publisher=get_publisher(request))


def get_gen_code_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)], request: Request) -> GenerateVerificationCodeUseCase:
    return GenerateVerificationCodeUseCase(repo=repo, code_repo=code_repo, publisher=get_publisher(request))


def get_verify_code_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], code_repo: Annotated[VerificationCodeRepositoryProtocol, Depends(get_code_repo)], request: Request) -> VerifyVerificationCodeUseCase:
    return VerifyVerificationCodeUseCase(repo=repo, code_repo=code_repo, publisher=get_publisher(request))


def get_upload_proof_uc(repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)], proof_repo: Annotated[ProofImageRepositoryProtocol, Depends(get_proof_repo)], request: Request) -> UploadProofUseCase:
    return UploadProofUseCase(repo=repo, proof_repo=proof_repo, publisher=get_publisher(request))


def get_nearby_drivers_uc(request: Request) -> FindNearbyDriversUseCase:
    return FindNearbyDriversUseCase(geo=get_geo(request), cache=get_cache(request), publisher=get_publisher(request))


def get_broadcast_uc(request: Request) -> BroadcastRideToDriversUseCase:
    return BroadcastRideToDriversUseCase(cache=get_cache(request), ws=get_ws_manager(request), webhook=get_webhook(request), publisher=get_publisher(request))


def get_gen_proof_url_uc(
    request: Request,
    repo: Annotated[ServiceRequestRepositoryProtocol, Depends(get_ride_repo)],
) -> GenerateProofUploadUrlUseCase:
    return GenerateProofUploadUrlUseCase(repo=repo, storage=get_storage(request))


def get_proof_with_url_uc(
    request: Request,
    proof_repo: Annotated[ProofImageRepositoryProtocol, Depends(get_proof_repo)],
) -> GetProofWithUrlUseCase:
    return GetProofWithUrlUseCase(proof_repo=proof_repo, storage=get_storage(request))
