"""Ride service use cases — all orchestration lives here."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.events import (
    DriverMatchingCompletedEvent,
    DriverMatchingRequestedEvent,
    ServiceProofUploadedEvent,
    ServiceRequestAcceptedEvent,
    ServiceRequestCancelledEvent,
    ServiceRequestCompletedEvent,
    ServiceRequestCreatedEvent,
    ServiceRequestStartedEvent,
    ServiceStopArrivedEvent,
    ServiceStopCompletedEvent,
    ServiceVerificationGeneratedEvent,
    ServiceVerificationVerifiedEvent,
)
from sp.infrastructure.messaging.publisher import EventPublisher

from ..domain.exceptions import (
    RideNotFoundError,
    StopNotFoundError,
    UnauthorisedRideAccessError,
    VerificationCodeNotFoundError,
)
from ..domain.interfaces import (
    GeospatialClientProtocol,
    ProofImageRepositoryProtocol,
    ServiceRequestRepositoryProtocol,
    StopRepositoryProtocol,
    VerificationCodeRepositoryProtocol,
    WebhookClientProtocol,
)
from ..domain.models import (
    DriverCandidate,
    ProofImage,
    RideStatus,
    ServiceRequest,
    Stop,
    VerificationCode,
)
from .schemas import (
    AcceptRideRequest,
    AddStopRequest,
    CancelRideRequest,
    CreateRideRequest,
    DriverCandidateResponse,
    GenerateVerificationCodeRequest,
    NearbyDriversResponse,
    ProofImageResponse,
    RideResponse,
    RideSummaryResponse,
    StopResponse,
    UploadProofRequest,
    VerificationCodeResponse,
    VerifyAndCompleteRequest,
    VerifyAndStartRequest,
    VerifyCodeRequest,
)
from ..infrastructure.websocket_manager import DriverEvent, PassengerEvent, WebSocketManager

logger = logging.getLogger("ride.use_cases")

_RIDE_CACHE_NS = "ride"
_RIDE_CACHE_TTL = 1800          # 30 min
_CANDIDATES_NS = "ride:candidates"
_CANDIDATES_TTL = 600           # 10 min


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _stop_to_resp(s: Stop) -> StopResponse:
    return StopResponse(
        id=s.id, service_request_id=s.service_request_id,
        sequence_order=s.sequence_order, stop_type=s.stop_type,
        latitude=s.latitude, longitude=s.longitude,
        place_name=s.place_name, address_line_1=s.address_line_1,
        address_line_2=s.address_line_2, city=s.city, state=s.state,
        country=s.country, postal_code=s.postal_code,
        contact_name=s.contact_name, contact_phone=s.contact_phone,
        instructions=s.instructions, arrived_at=s.arrived_at,
        completed_at=s.completed_at,
    )


def _proof_to_resp(p: ProofImage) -> ProofImageResponse:
    return ProofImageResponse(
        id=p.id, service_request_id=p.service_request_id, stop_id=p.stop_id,
        proof_type=p.proof_type, file_key=p.file_key, file_name=p.file_name,
        mime_type=p.mime_type, file_size_bytes=p.file_size_bytes,
        is_primary=p.is_primary, uploaded_by_user_id=p.uploaded_by_user_id,
        uploaded_by_driver_id=p.uploaded_by_driver_id, uploaded_at=p.uploaded_at,
    )


def _code_to_resp(c: VerificationCode) -> VerificationCodeResponse:
    return VerificationCodeResponse(
        id=c.id, service_request_id=c.service_request_id, stop_id=c.stop_id,
        is_verified=c.is_verified, attempts=c.attempts, max_attempts=c.max_attempts,
        expires_at=c.expires_at, generated_at=c.generated_at, verified_at=c.verified_at,
    )


def _ride_to_resp(ride: ServiceRequest) -> RideResponse:
    pickup = ride.pickup_stop
    dropoff = ride.dropoff_stop
    return RideResponse(
        id=ride.id, passenger_id=ride.passenger_id,
        assigned_driver_id=ride.assigned_driver_id,
        service_type=ride.service_type, category=ride.category,
        pricing_mode=ride.pricing_mode, status=ride.status,
        baseline_min_price=ride.baseline_min_price,
        baseline_max_price=ride.baseline_max_price,
        final_price=ride.final_price, scheduled_at=ride.scheduled_at,
        is_scheduled=ride.is_scheduled, is_risky=ride.is_risky,
        auto_accept_driver=ride.auto_accept_driver,
        accepted_at=ride.accepted_at, completed_at=ride.completed_at,
        cancelled_at=ride.cancelled_at, cancellation_reason=ride.cancellation_reason,
        created_at=ride.created_at,
        stops=[_stop_to_resp(s) for s in ride.stops],
        proof_images=[_proof_to_resp(p) for p in ride.proof_images],
        verification_codes=[_code_to_resp(c) for c in ride.verification_codes],
        pickup_stop=_stop_to_resp(pickup) if pickup else None,
        dropoff_stop=_stop_to_resp(dropoff) if dropoff else None,
    )


def _ride_to_summary(ride: ServiceRequest) -> RideSummaryResponse:
    pickup = ride.pickup_stop
    dropoff = ride.dropoff_stop
    return RideSummaryResponse(
        id=ride.id, passenger_id=ride.passenger_id,
        assigned_driver_id=ride.assigned_driver_id,
        service_type=ride.service_type, category=ride.category,
        status=ride.status, created_at=ride.created_at,
        scheduled_at=ride.scheduled_at,
        pickup_stop=_stop_to_resp(pickup) if pickup else None,
        dropoff_stop=_stop_to_resp(dropoff) if dropoff else None,
    )


async def _publish(pub: EventPublisher | None, event: object) -> None:
    if pub:
        await pub.publish(event)  # type: ignore[arg-type]


async def _cache_ride(cache: CacheManager, ride: ServiceRequest) -> None:
    await cache.set(_RIDE_CACHE_NS, str(ride.id), {
        "id": str(ride.id), "status": ride.status.value,
        "passenger_id": str(ride.passenger_id),
        "assigned_driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
        "service_type": ride.service_type.value,
    }, ttl=_RIDE_CACHE_TTL)


async def _load_ride_or_404(
    repo: ServiceRequestRepositoryProtocol, ride_id: UUID
) -> ServiceRequest:
    ride = await repo.find_by_id(ride_id)
    if not ride:
        raise RideNotFoundError(f"Ride {ride_id} not found.")
    return ride


# ---------------------------------------------------------------------------
# Phase 1: Create
# ---------------------------------------------------------------------------

class CreateRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, cmd: CreateRideRequest, passenger_id: UUID) -> RideResponse:
        ride = ServiceRequest.create(
            passenger_id=passenger_id,
            service_type=cmd.service_type,
            category=cmd.category,
            pricing_mode=cmd.pricing_mode,
            baseline_min_price=cmd.baseline_min_price,
            baseline_max_price=cmd.baseline_max_price,
            scheduled_at=cmd.scheduled_at,
            auto_accept_driver=cmd.auto_accept_driver,
        )
        stops = [
            Stop.create(
                service_request_id=ride.id,
                sequence_order=s.sequence_order,
                stop_type=s.stop_type,
                latitude=s.latitude,
                longitude=s.longitude,
                place_name=s.place_name,
                address_line_1=s.address_line_1,
                address_line_2=s.address_line_2,
                city=s.city,
                state=s.state,
                country=s.country,
                postal_code=s.postal_code,
                contact_name=s.contact_name,
                contact_phone=s.contact_phone,
                instructions=s.instructions,
            )
            for s in sorted(cmd.stops, key=lambda x: x.sequence_order)
        ]
        detail_data = cmd.detail.model_dump(mode="python")
        ride = await self._repo.create_full(ride, stops, detail_data)

        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestCreatedEvent(payload={
            "ride_id": str(ride.id),
            "passenger_id": str(ride.passenger_id),
            "service_type": ride.service_type.value,
            "category": ride.category.value,
        }))
        await self._ws.broadcast_to_passenger(
            passenger_id, PassengerEvent.RIDE_CREATED,
            {"ride_id": str(ride.id), "status": ride.status.value},
        )
        logger.info("Ride created ride_id=%s passenger=%s", ride.id, passenger_id)
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 1: Read
# ---------------------------------------------------------------------------

class GetRideUseCase:
    def __init__(self, repo: ServiceRequestRepositoryProtocol, cache: CacheManager) -> None:
        self._repo = repo
        self._cache = cache

    async def execute(self, ride_id: UUID) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        await _cache_ride(self._cache, ride)
        return _ride_to_resp(ride)


class ListPassengerRidesUseCase:
    def __init__(self, repo: ServiceRequestRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(
        self,
        passenger_id: UUID,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RideSummaryResponse]:
        rides = await self._repo.find_by_passenger(
            passenger_id, status_filter=status_filter, limit=limit, offset=offset
        )
        return [_ride_to_summary(r) for r in rides]


# ---------------------------------------------------------------------------
# Phase 2: Cancel
# ---------------------------------------------------------------------------

class CancelRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: CancelRideRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        ride.cancel(cmd.reason)
        await self._repo.update_status(
            ride.id, ride.status,
            cancelled_at=ride.cancelled_at,
            cancellation_reason=ride.cancellation_reason,
        )
        await self._cache.delete(_RIDE_CACHE_NS, str(ride_id))
        await _publish(self._pub, ServiceRequestCancelledEvent(payload={
            "ride_id": str(ride.id), "reason": cmd.reason,
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_CANCELLED,
            {"ride_id": str(ride.id), "reason": cmd.reason},
        )
        if ride.assigned_driver_id:
            await self._ws.broadcast_to_driver(
                ride.assigned_driver_id, DriverEvent.JOB_CANCELLED,
                {"ride_id": str(ride.id)},
            )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 2: Accept
# ---------------------------------------------------------------------------

class AcceptRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: AcceptRideRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        ride.accept(cmd.driver_id)
        await self._repo.update_status(
            ride.id, ride.status,
            accepted_at=ride.accepted_at,
            assigned_driver_id=ride.assigned_driver_id,
        )
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestAcceptedEvent(payload={
            "ride_id": str(ride.id), "driver_id": str(cmd.driver_id),
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.DRIVER_ASSIGNED,
            {"ride_id": str(ride.id), "driver_id": str(cmd.driver_id)},
        )
        await self._ws.broadcast_to_driver(
            cmd.driver_id, DriverEvent.JOB_ASSIGNED,
            {"ride_id": str(ride.id)},
        )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 2: Start
# ---------------------------------------------------------------------------

class StartRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: VerifyAndStartRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.assigned_driver_id != cmd.driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        if cmd.verification_code:
            code = await self._code_repo.find_active_by_ride(ride_id)
            if not code:
                raise VerificationCodeNotFoundError("No active verification code found.")
            code.verify(cmd.verification_code, driver_id=cmd.driver_id)
            await self._code_repo.update_verification(code)
        ride.start()
        await self._repo.update_status(ride.id, ride.status)
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestStartedEvent(payload={"ride_id": str(ride.id)}))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_STARTED, {"ride_id": str(ride.id)}
        )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 2: Complete
# ---------------------------------------------------------------------------

class CompleteRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: VerifyAndCompleteRequest) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.assigned_driver_id != cmd.driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        if cmd.verification_code:
            code = await self._code_repo.find_active_by_ride(ride_id)
            if not code:
                raise VerificationCodeNotFoundError("No active verification code for completion.")
            code.verify(cmd.verification_code, driver_id=cmd.driver_id)
            await self._code_repo.update_verification(code)
        ride.complete()
        await self._repo.update_status(
            ride.id, ride.status,
            completed_at=ride.completed_at,
            final_price=cmd.final_price,
        )
        await self._cache.delete(_RIDE_CACHE_NS, str(ride_id))
        await _publish(self._pub, ServiceRequestCompletedEvent(payload={
            "ride_id": str(ride.id), "final_price": cmd.final_price,
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_COMPLETED,
            {"ride_id": str(ride.id), "final_price": cmd.final_price},
        )
        return _ride_to_resp(ride)


# ---------------------------------------------------------------------------
# Phase 3: Stops
# ---------------------------------------------------------------------------

class AddStopUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        stop_repo: StopRepositoryProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._stop_repo = stop_repo
        self._ws = ws
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: "AddStopRequest") -> StopResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if not ride.is_active:
            raise RideNotFoundError("Cannot add stops to an inactive ride.")
        stop = Stop.create(
            service_request_id=ride_id,
            sequence_order=cmd.sequence_order,
            stop_type=cmd.stop_type,
            latitude=cmd.latitude,
            longitude=cmd.longitude,
            place_name=cmd.place_name,
            address_line_1=cmd.address_line_1,
            city=cmd.city,
            country=cmd.country,
            contact_name=cmd.contact_name,
            contact_phone=cmd.contact_phone,
            instructions=cmd.instructions,
        )
        stop = await self._stop_repo.create(stop)
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.STOP_UPDATED,
            {"ride_id": str(ride_id), "stop_id": str(stop.id), "action": "added"},
        )
        return _stop_to_resp(stop)


class MarkStopArrivedUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        stop_repo: StopRepositoryProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._stop_repo = stop_repo
        self._ws = ws
        self._pub = publisher

    async def execute(self, stop_id: UUID, driver_id: UUID) -> StopResponse:
        stop = await self._stop_repo.find_by_id(stop_id)
        if not stop:
            raise StopNotFoundError(f"Stop {stop_id} not found.")
        ride = await _load_ride_or_404(self._repo, stop.service_request_id)
        if ride.assigned_driver_id != driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        stop.mark_arrived()
        await self._stop_repo.update_arrived_at(stop_id, stop.arrived_at)  # type: ignore[arg-type]
        if ride.status == RideStatus.ACCEPTED:
            ride.driver_arriving()
            await self._repo.update_status(ride.id, ride.status)
        await _publish(self._pub, ServiceStopArrivedEvent(payload={
            "stop_id": str(stop_id), "ride_id": str(ride.id),
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.STOP_UPDATED,
            {"ride_id": str(ride.id), "stop_id": str(stop_id), "action": "arrived"},
        )
        return _stop_to_resp(stop)


class MarkStopCompletedUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        stop_repo: StopRepositoryProtocol,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._stop_repo = stop_repo
        self._ws = ws
        self._pub = publisher

    async def execute(self, stop_id: UUID, driver_id: UUID) -> StopResponse:
        stop = await self._stop_repo.find_by_id(stop_id)
        if not stop:
            raise StopNotFoundError(f"Stop {stop_id} not found.")
        ride = await _load_ride_or_404(self._repo, stop.service_request_id)
        if ride.assigned_driver_id != driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")
        stop.mark_completed()
        await self._stop_repo.update_completed_at(stop_id, stop.completed_at)  # type: ignore[arg-type]
        await _publish(self._pub, ServiceStopCompletedEvent(payload={
            "stop_id": str(stop_id), "ride_id": str(ride.id),
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.STOP_UPDATED,
            {"ride_id": str(ride.id), "stop_id": str(stop_id), "action": "completed"},
        )
        return _stop_to_resp(stop)


# ---------------------------------------------------------------------------
# Phase 4: Verification Codes
# ---------------------------------------------------------------------------

class GenerateVerificationCodeUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._pub = publisher

    async def execute(
        self, ride_id: UUID, cmd: GenerateVerificationCodeRequest
    ) -> VerificationCodeResponse:
        await _load_ride_or_404(self._repo, ride_id)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=cmd.expires_in_minutes)
        code = VerificationCode.generate(
            service_request_id=ride_id,
            stop_id=cmd.stop_id,
            expires_at=expires_at,
            length=cmd.length,
            max_attempts=cmd.max_attempts,
        )
        await self._code_repo.create(code)
        await _publish(self._pub, ServiceVerificationGeneratedEvent(payload={
            "ride_id": str(ride_id), "code_id": str(code.id),
        }))
        return _code_to_resp(code)


class VerifyVerificationCodeUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        code_repo: VerificationCodeRepositoryProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: VerifyCodeRequest) -> VerificationCodeResponse:
        await _load_ride_or_404(self._repo, ride_id)
        code = await self._code_repo.find_active_by_ride(ride_id)
        if not code:
            raise VerificationCodeNotFoundError("No active verification code found.")
        code.verify(cmd.code, user_id=cmd.user_id, driver_id=cmd.driver_id)
        await self._code_repo.update_verification(code)
        await _publish(self._pub, ServiceVerificationVerifiedEvent(payload={
            "ride_id": str(ride_id), "code_id": str(code.id),
        }))
        return _code_to_resp(code)


# ---------------------------------------------------------------------------
# Phase 4: Proof Upload
# ---------------------------------------------------------------------------

class UploadProofUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        proof_repo: ProofImageRepositoryProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._proof_repo = proof_repo
        self._pub = publisher

    async def execute(self, ride_id: UUID, cmd: UploadProofRequest) -> ProofImageResponse:
        await _load_ride_or_404(self._repo, ride_id)
        proof = ProofImage.create(
            service_request_id=ride_id,
            proof_type=cmd.proof_type,
            file_key=cmd.file_key,
            uploaded_by_user_id=cmd.uploaded_by_user_id,
            uploaded_by_driver_id=cmd.uploaded_by_driver_id,
            stop_id=cmd.stop_id,
            file_name=cmd.file_name,
            mime_type=cmd.mime_type,
            file_size_bytes=cmd.file_size_bytes,
            checksum_sha256=cmd.checksum_sha256,
            is_primary=cmd.is_primary,
        )
        await self._proof_repo.create(proof)
        await _publish(self._pub, ServiceProofUploadedEvent(payload={
            "ride_id": str(ride_id), "proof_id": str(proof.id),
            "proof_type": proof.proof_type.value,
        }))
        return _proof_to_resp(proof)


# ---------------------------------------------------------------------------
# Phase 5: Matching & Broadcasting
# ---------------------------------------------------------------------------

class FindNearbyDriversUseCase:
    def __init__(
        self,
        geo: GeospatialClientProtocol,
        cache: CacheManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._geo = geo
        self._cache = cache
        self._pub = publisher

    async def execute(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        ride_id: UUID | None = None,
        category: str | None = None,
        vehicle_type: str | None = None,
        fuel_types: list[str] | None = None,
        limit: int = 20,
    ) -> NearbyDriversResponse:
        candidates = await self._geo.find_nearby_drivers(
            latitude, longitude, radius_km,
            category=category, vehicle_type=vehicle_type,
            fuel_types=fuel_types, limit=limit,
        )
        if ride_id:
            await self._cache.set(
                _CANDIDATES_NS, str(ride_id),
                [{"driver_id": str(c.driver_id), "distance_km": c.distance_km,
                  "vehicle_type": c.vehicle_type, "priority_score": c.priority_score}
                 for c in candidates],
                ttl=_CANDIDATES_TTL,
            )
        await _publish(self._pub, DriverMatchingRequestedEvent(payload={
            "ride_id": str(ride_id) if ride_id else None,
            "candidate_count": len(candidates),
        }))
        return NearbyDriversResponse(
            ride_id=ride_id,
            candidates=[
                DriverCandidateResponse(
                    driver_id=c.driver_id, distance_km=c.distance_km,
                    vehicle_type=c.vehicle_type, rating=c.rating,
                    priority_score=c.priority_score,
                    estimated_arrival_minutes=c.estimated_arrival_minutes,
                )
                for c in candidates
            ],
            count=len(candidates),
        )


class BroadcastRideToDriversUseCase:
    def __init__(
        self,
        cache: CacheManager,
        ws: WebSocketManager,
        webhook: WebhookClientProtocol,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._cache = cache
        self._ws = ws
        self._webhook = webhook
        self._pub = publisher

    async def execute(
        self,
        ride_id: UUID,
        candidates: list[DriverCandidate],
        ride_payload: dict,
    ) -> None:
        driver_ids = [c.driver_id for c in candidates]
        await self._ws.broadcast_to_drivers(
            driver_ids, DriverEvent.NEW_JOB,
            {"ride_id": str(ride_id), **ride_payload},
        )
        for c in candidates:
            await self._webhook.dispatch_ride_job(
                c.driver_id, ride_id, ride_payload,
                idempotency_key=f"{ride_id}:{c.driver_id}",
            )
        await _publish(self._pub, DriverMatchingCompletedEvent(payload={
            "ride_id": str(ride_id), "dispatched_to": len(driver_ids),
        }))
        logger.info("Ride broadcast ride_id=%s drivers=%d", ride_id, len(driver_ids))


# ---------------------------------------------------------------------------
# Phase 4b: Proof image presigned URL generation
# ---------------------------------------------------------------------------

class GenerateProofUploadUrlUseCase:
    """
    Step 1 of the proof upload flow — generate a presigned S3 PUT URL.

    The client uses the returned URL to upload the binary directly to S3.
    After a successful upload the client calls UploadProofUseCase (step 3)
    with the returned file_key to register the proof metadata.
    """

    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        storage: "S3StorageProvider",
    ) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(
        self,
        ride_id: UUID,
        cmd: "ProofUploadUrlRequest",
    ) -> "ProofUploadUrlResponse":
        from .schemas import ProofUploadUrlResponse
        from ..infrastructure.storage import build_proof_key

        await _load_ride_or_404(self._repo, ride_id)

        file_key = build_proof_key(ride_id, cmd.proof_type.value, cmd.file_name)
        presigned_url = await self._storage.generate_presigned_put_url(
            file_key,
            content_type=cmd.mime_type,
        )
        logger.info(
            "Generated proof upload URL ride_id=%s proof_type=%s key=%s",
            ride_id, cmd.proof_type.value, file_key,
        )
        return ProofUploadUrlResponse(
            presigned_url=presigned_url,
            file_key=file_key,
            expires_in_seconds=900,
            proof_type=cmd.proof_type,
            mime_type=cmd.mime_type,
        )


class GetProofWithUrlUseCase:
    """
    Retrieve a proof image record and enrich it with a presigned GET URL
    so the client can display/download the image without making the S3
    bucket public.
    """

    def __init__(
        self,
        proof_repo: ProofImageRepositoryProtocol,
        storage: "S3StorageProvider",
    ) -> None:
        self._proof_repo = proof_repo
        self._storage = storage

    async def execute(
        self,
        ride_id: UUID,
        proof_id: UUID,
    ) -> "ProofImageWithUrlResponse":
        from .schemas import ProofImageWithUrlResponse

        proofs = await self._proof_repo.find_by_ride(ride_id)
        proof = next((p for p in proofs if p.id == proof_id), None)
        if proof is None:
            from ..domain.exceptions import RideNotFoundError
            raise RideNotFoundError(f"Proof {proof_id} not found on ride {ride_id}.")

        view_url = await self._storage.generate_presigned_get_url(proof.file_key)

        return ProofImageWithUrlResponse(
            id=proof.id,
            service_request_id=proof.service_request_id,
            stop_id=proof.stop_id,
            proof_type=proof.proof_type,
            file_key=proof.file_key,
            file_name=proof.file_name,
            mime_type=proof.mime_type,
            file_size_bytes=proof.file_size_bytes,
            is_primary=proof.is_primary,
            uploaded_by_user_id=proof.uploaded_by_user_id,
            uploaded_by_driver_id=proof.uploaded_by_driver_id,
            uploaded_at=proof.uploaded_at,
            view_url=view_url,
        )
