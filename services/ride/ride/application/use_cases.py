"""Ride service use cases — all orchestration lives here."""
from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
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

if TYPE_CHECKING:
    from ..infrastructure.storage import S3StorageProvider
    from .schemas import (
        ProofImageWithUrlResponse,
        ProofUploadUrlRequest,
        ProofUploadUrlResponse,
    )

from ..domain.exceptions import (
    InvalidStateTransitionError,
    RideCompletionLocationError,
    RideDomainError,
    RideNotFoundError,
    StopNotFoundError,
    UnauthorisedRideAccessError,
    VerificationCodeNotFoundError,
)
from ..domain.interfaces import (
    GeospatialClientProtocol,
    PaymentClientProtocol,
    ProofImageRepositoryProtocol,
    ServiceRequestRepositoryProtocol,
    StopRepositoryProtocol,
    VerificationCodeRepositoryProtocol,
    WebhookClientProtocol,
)
from ..domain.models import (
    DriverCandidate,
    PricingMode,
    ProofImage,
    RideStatus,
    ServiceRequest,
    Stop,
    StopType,
    VerificationCode,
)
from ..infrastructure.websocket_manager import DriverEvent, PassengerEvent, WebSocketManager
from .schemas import (
    AcceptRideRequest,
    AddStopRequest,
    CancelRideRequest,
    CreateRideRequest,
    DriverActiveRideResponse,
    DriverCandidateResponse,
    DriverRideRequestResponse,
    DriverRouteSummaryResponse,
    GenerateVerificationCodeRequest,
    NearbyDriversResponse,
    ProofImageResponse,
    ProofImageWithUrlResponse,
    ProofUploadUrlResponse,
    RecentRideDestinationResponse,
    RideResponse,
    RideSummaryResponse,
    StopResponse,
    UploadProofRequest,
    VerificationCodeResponse,
    VerifyAndCompleteRequest,
    VerifyAndStartRequest,
    VerifyCodeRequest,
)

logger = logging.getLogger("ride.use_cases")

_RIDE_CACHE_NS = "ride"
_RIDE_CACHE_TTL = 1800          # 30 min
_CANDIDATES_NS = "ride:candidates"
_CANDIDATES_TTL = 600           # 10 min
_COMPLETE_DESTINATION_RADIUS_METERS = 15.0


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
        final_price=ride.final_price,
        passenger_payment_method=ride.passenger_payment_method,
        passenger_payment_method_id=ride.passenger_payment_method_id,
        payment_collection_mode=ride.payment_collection_mode,
        scheduled_at=ride.scheduled_at,
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
        pricing_mode=ride.pricing_mode,
        status=ride.status,
        passenger_payment_method=ride.passenger_payment_method,
        payment_collection_mode=ride.payment_collection_mode,
        created_at=ride.created_at,
        scheduled_at=ride.scheduled_at,
        pickup_stop=_stop_to_resp(pickup) if pickup else None,
        dropoff_stop=_stop_to_resp(dropoff) if dropoff else None,
    )


def _ride_to_recent_destination(ride: ServiceRequest) -> RecentRideDestinationResponse | None:
    dropoff = ride.dropoff_stop
    if dropoff is None:
        return None
    return RecentRideDestinationResponse(
        ride_id=ride.id,
        service_type=ride.service_type,
        category=ride.category,
        pricing_mode=ride.pricing_mode,
        created_at=ride.created_at,
        pickup_stop=_stop_to_resp(ride.pickup_stop) if ride.pickup_stop else None,
        dropoff_stop=_stop_to_resp(dropoff),
    )


def _route_to_resp(route: dict | None) -> DriverRouteSummaryResponse | None:
    if not route:
        return None
    return DriverRouteSummaryResponse(
        distance_km=float(route.get("distance_km") or 0),
        duration_minutes=float(route.get("duration_minutes") or 0),
        polyline=route.get("polyline"),
    )


def _distance_km(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> float:
    radius_km = 6371.0
    lat1 = math.radians(origin_latitude)
    lat2 = math.radians(destination_latitude)
    d_lat = math.radians(destination_latitude - origin_latitude)
    d_lng = math.radians(destination_longitude - origin_longitude)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _distance_meters(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> float:
    return _distance_km(
        origin_latitude,
        origin_longitude,
        destination_latitude,
        destination_longitude,
    ) * 1000


async def _driver_request_to_resp(
    ride: ServiceRequest,
    geo: GeospatialClientProtocol | None,
    driver_latitude: float | None = None,
    driver_longitude: float | None = None,
) -> DriverRideRequestResponse:
    pickup = ride.pickup_stop
    dropoff = ride.dropoff_stop
    driver_route = None
    trip_route = None
    if geo and pickup and driver_latitude is not None and driver_longitude is not None:
        driver_route = await geo.calculate_route(
            driver_latitude,
            driver_longitude,
            pickup.latitude,
            pickup.longitude,
        )
    if geo and pickup and dropoff:
        trip_route = await geo.calculate_route(
            pickup.latitude,
            pickup.longitude,
            dropoff.latitude,
            dropoff.longitude,
        )
    return DriverRideRequestResponse(
        id=ride.id,
        passenger_id=ride.passenger_id,
        service_type=ride.service_type,
        category=ride.category,
        pricing_mode=ride.pricing_mode,
        status=ride.status,
        baseline_min_price=ride.baseline_min_price,
        baseline_max_price=ride.baseline_max_price,
        final_price=ride.final_price,
        passenger_payment_method=ride.passenger_payment_method,
        payment_collection_mode=ride.payment_collection_mode,
        created_at=ride.created_at,
        pickup_stop=_stop_to_resp(pickup) if pickup else None,
        dropoff_stop=_stop_to_resp(dropoff) if dropoff else None,
        driver_to_pickup=_route_to_resp(driver_route),
        trip_route=_route_to_resp(trip_route),
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


async def _ensure_driver_has_no_active_ride(
    repo: ServiceRequestRepositoryProtocol,
    driver_id: UUID,
) -> None:
    active_ride = await repo.find_active_by_driver(driver_id)
    if active_ride:
        raise RideDomainError(
            f"Driver {driver_id} already has active ride {active_ride.id}."
        )


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
        payment: PaymentClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher
        self._payment = payment

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
            passenger_payment_method=cmd.passenger_payment_method,
            passenger_payment_method_id=cmd.passenger_payment_method_id,
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
        if self._payment:
            await self._payment.create_ride_payment(
                ride.id,
                ride.passenger_id,
                ride.passenger_payment_method.value,
                ride.passenger_payment_method_id,
                ride.baseline_min_price or ride.baseline_max_price,
                idempotency_key=f"ride_payment:{ride.id}",
            )

        # Enter MATCHING state so ride can be accepted (FIXED mode) or enter bidding (BID/HYBRID)
        ride.begin_matching()
        await self._repo.update_status(ride.id, ride.status)

        await _cache_ride(self._cache, ride)
        # Extract matching data for geospatial service
        pickup_stop = next((s for s in stops if s.stop_type == StopType.PICKUP), None)
        dropoff_stop = next((s for s in stops if s.stop_type == StopType.DROPOFF), None)
        vehicle_type = getattr(cmd.detail, "preferred_vehicle_type", None)
        if hasattr(cmd.detail, "vehicle_type_requested"):
             vehicle_type = cmd.detail.vehicle_type_requested
        elif hasattr(cmd.detail, "vehicle_type"):
             vehicle_type = cmd.detail.vehicle_type

        await _publish(self._pub, ServiceRequestCreatedEvent(payload={
            "ride_id": str(ride.id),
            "passenger_id": str(ride.passenger_id),
            "passenger_user_id": str(ride.passenger_id),
            "service_type": ride.service_type.value,
            "category": ride.category.value,
            "pricing_mode": ride.pricing_mode.value,
            "baseline_min_price": float(ride.baseline_min_price) if ride.baseline_min_price is not None else None,
            "baseline_max_price": float(ride.baseline_max_price) if ride.baseline_max_price is not None else None,
            "auto_accept_driver": ride.auto_accept_driver,
            "pickup_latitude": pickup_stop.latitude if pickup_stop else 0.0,
            "pickup_longitude": pickup_stop.longitude if pickup_stop else 0.0,
            "dropoff_latitude": dropoff_stop.latitude if dropoff_stop else None,
            "dropoff_longitude": dropoff_stop.longitude if dropoff_stop else None,
            "vehicle_type": vehicle_type.value if vehicle_type else None,
            "matching_radius_km": 5.0,
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


class ListRecentRideDestinationsUseCase:
    def __init__(self, repo: ServiceRequestRepositoryProtocol) -> None:
        self._repo = repo

    async def execute(
        self,
        passenger_id: UUID,
        *,
        limit: int = 5,
    ) -> list[RecentRideDestinationResponse]:
        rides = await self._repo.find_by_passenger(
            passenger_id,
            status_filter=[RideStatus.COMPLETED],
            limit=max(limit * 4, limit),
            offset=0,
        )
        destinations: list[RecentRideDestinationResponse] = []
        seen: set[tuple[int, int, str]] = set()
        for ride in rides:
            item = _ride_to_recent_destination(ride)
            if item is None:
                continue
            stop = item.dropoff_stop
            key = (
                round(stop.latitude * 100000),
                round(stop.longitude * 100000),
                (stop.place_name or stop.address_line_1 or "").strip().casefold(),
            )
            if key in seen:
                continue
            seen.add(key)
            destinations.append(item)
            if len(destinations) >= limit:
                break
        return destinations


class ListDriverRequestsUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        geo: GeospatialClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._geo = geo

    async def execute(
        self,
        driver_id: UUID,
        *,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 20,
    ) -> list[DriverRideRequestResponse]:
        rides = await self._repo.find_available_for_driver(driver_id, limit=max(limit * 3, 25))
        nearby: list[ServiceRequest] = []
        for ride in rides:
            pickup = ride.pickup_stop
            if not pickup:
                continue
            if _distance_km(latitude, longitude, pickup.latitude, pickup.longitude) <= radius_km:
                nearby.append(ride)
            if len(nearby) >= limit:
                break
        return [
            await _driver_request_to_resp(
                ride,
                self._geo,
                driver_latitude=latitude,
                driver_longitude=longitude,
            )
            for ride in nearby
        ]


class GetDriverActiveRideUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        geo: GeospatialClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._geo = geo

    async def execute(
        self,
        driver_id: UUID,
        *,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> DriverActiveRideResponse | None:
        ride = await self._repo.find_active_by_driver(driver_id)
        if not ride:
            return None
        pickup = ride.pickup_stop
        dropoff = ride.dropoff_stop
        driver_route = None
        trip_route = None
        if self._geo and pickup and latitude is not None and longitude is not None:
            driver_route = await self._geo.calculate_route(
                latitude,
                longitude,
                pickup.latitude,
                pickup.longitude,
            )
        if self._geo and pickup and dropoff:
            trip_route = await self._geo.calculate_route(
                pickup.latitude,
                pickup.longitude,
                dropoff.latitude,
                dropoff.longitude,
            )
        data = _ride_to_resp(ride).model_dump()
        data["driver_to_pickup"] = _route_to_resp(driver_route)
        data["trip_route"] = _route_to_resp(trip_route)
        return DriverActiveRideResponse(**data)


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
        payment: PaymentClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher
        self._payment = payment

    async def execute(self, ride_id: UUID, cmd: CancelRideRequest, passenger_id: UUID) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.passenger_id != passenger_id:
            raise UnauthorisedRideAccessError(
                "Only the passenger who created this ride may cancel it."
            )
        ride.cancel(cmd.reason)
        if self._payment:
            await self._payment.release_commission(
                ride.id,
                ride.assigned_driver_id,
                cmd.reason,
                idempotency_key=f"commission_release:cancel:{ride.id}",
            )
        await self._repo.update_status(
            ride.id, ride.status,
            cancelled_at=ride.cancelled_at,
            cancellation_reason=ride.cancellation_reason,
        )
        await self._cache.delete(_RIDE_CACHE_NS, str(ride_id))
        await _publish(self._pub, ServiceRequestCancelledEvent(payload={
            "ride_id": str(ride.id),
            "passenger_user_id": str(ride.passenger_id),
            "assigned_driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
            "driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
            "reason": cmd.reason,
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
        payment: PaymentClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher
        self._payment = payment

    async def execute(self, ride_id: UUID, cmd: AcceptRideRequest, driver_id: UUID) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        # FIXED mode only - BID_BASED/HYBRID must go through bidding service
        if ride.pricing_mode != PricingMode.FIXED:
            raise InvalidStateTransitionError(
                f"Direct accept not allowed for {ride.pricing_mode.value} pricing. "
                f"Use the Bidding Service (POST /bidding/sessions/{{id}}/bids) instead."
            )
        await _ensure_driver_has_no_active_ride(self._repo, driver_id)
        if self._payment:
            basis_amount = ride.baseline_min_price or ride.baseline_max_price or ride.final_price or 0.0
            await self._payment.reserve_commission(
                ride.id,
                driver_id,
                ride.passenger_id,
                basis_amount,
                idempotency_key=f"commission_reserve:fixed:{ride.id}:{driver_id}",
            )
        ride.accept(driver_id)
        await self._repo.update_status(
            ride.id, ride.status,
            accepted_at=ride.accepted_at,
            assigned_driver_id=ride.assigned_driver_id,
        )
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestAcceptedEvent(payload={
            "ride_id": str(ride.id),
            "passenger_user_id": str(ride.passenger_id),
            "driver_id": str(driver_id),
            "pricing_mode": ride.pricing_mode.value,
            "final_price": ride.final_price,
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.DRIVER_ASSIGNED,
            {"ride_id": str(ride.id), "driver_id": str(driver_id)},
        )
        await self._ws.broadcast_to_driver(
            driver_id, DriverEvent.JOB_ASSIGNED,
            {"ride_id": str(ride.id)},
        )
        return _ride_to_resp(ride)


class InternalAssignDriverUseCase:
    def __init__(
        self,
        repo: ServiceRequestRepositoryProtocol,
        cache: CacheManager,
        ws: WebSocketManager,
        publisher: EventPublisher | None = None,
        payment: PaymentClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher
        self._payment = payment

    async def execute(self, ride_id: UUID, driver_id: UUID, final_price: float | None = None) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        await _ensure_driver_has_no_active_ride(self._repo, driver_id)
        if self._payment and ride.pricing_mode == PricingMode.FIXED:
            basis_amount = final_price or ride.baseline_min_price or ride.baseline_max_price or ride.final_price or 0.0
            await self._payment.reserve_commission(
                ride.id,
                driver_id,
                ride.passenger_id,
                basis_amount,
                idempotency_key=f"commission_reserve:internal:{ride.id}:{driver_id}",
            )
        ride.accept(driver_id)
        if final_price is not None:
            ride.final_price = final_price

        await self._repo.update_status(
            ride.id, ride.status,
            accepted_at=ride.accepted_at,
            assigned_driver_id=ride.assigned_driver_id,
            final_price=final_price,
        )
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestAcceptedEvent(payload={
            "ride_id": str(ride.id), "driver_id": str(driver_id),
            "passenger_user_id": str(ride.passenger_id),  # consumed by Location Service
            "pricing_mode": ride.pricing_mode.value,
            "final_price": ride.final_price,
        }))

        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.DRIVER_ASSIGNED,
            {"ride_id": str(ride.id), "driver_id": str(driver_id)},
        )
        await self._ws.broadcast_to_driver(
            driver_id, DriverEvent.JOB_ASSIGNED,
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
        payment: PaymentClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher
        self._payment = payment

    async def execute(self, ride_id: UUID, cmd: VerifyAndStartRequest, driver_id: UUID) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.assigned_driver_id != driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")

        if ride.requires_otp_start and not cmd.verification_code:
            raise VerificationCodeNotFoundError("A verification code is required to start this ride.")

        if cmd.verification_code:
            code = await self._code_repo.find_active_by_ride(ride_id)
            if not code:
                raise VerificationCodeNotFoundError("No active verification code found.")
            code.verify(cmd.verification_code, driver_id=driver_id)
            await self._code_repo.update_verification(code)
        ride.start()
        await self._repo.update_status(ride.id, ride.status)
        await _cache_ride(self._cache, ride)
        await _publish(self._pub, ServiceRequestStartedEvent(payload={
            "ride_id": str(ride.id),
            "passenger_user_id": str(ride.passenger_id),
            "driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
        }))
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
        payment: PaymentClientProtocol | None = None,
    ) -> None:
        self._repo = repo
        self._code_repo = code_repo
        self._cache = cache
        self._ws = ws
        self._pub = publisher
        self._payment = payment

    async def execute(self, ride_id: UUID, cmd: VerifyAndCompleteRequest, driver_id: UUID) -> RideResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.assigned_driver_id != driver_id:
            raise UnauthorisedRideAccessError("Driver is not assigned to this ride.")

        self._ensure_driver_is_at_dropoff(ride, cmd)

        if ride.requires_otp_end and not cmd.verification_code:
            raise VerificationCodeNotFoundError("A verification code is required to complete this ride.")

        if cmd.verification_code:
            code = await self._code_repo.find_active_by_ride(ride_id)
            if not code:
                raise VerificationCodeNotFoundError("No active verification code for completion.")
            code.verify(cmd.verification_code, driver_id=driver_id)
            await self._code_repo.update_verification(code)
        final_amount = cmd.final_price or ride.final_price or ride.baseline_min_price or ride.baseline_max_price or 0.0
        if self._payment:
            await self._payment.complete_ride_payment(
                ride.id,
                driver_id,
                final_amount,
                idempotency_key=f"ride_payment_complete:{ride.id}:{driver_id}",
            )
            await self._payment.capture_commission(
                ride.id,
                driver_id,
                final_amount,
                idempotency_key=f"commission_capture:{ride.id}:{driver_id}",
            )
        ride.complete()
        await self._repo.update_status(
            ride.id, ride.status,
            completed_at=ride.completed_at,
            final_price=final_amount,
        )
        await self._cache.delete(_RIDE_CACHE_NS, str(ride_id))
        await _publish(self._pub, ServiceRequestCompletedEvent(payload={
            "ride_id": str(ride.id),
            "passenger_user_id": str(ride.passenger_id),
            "assigned_driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
            "driver_id": str(ride.assigned_driver_id) if ride.assigned_driver_id else None,
            "final_price": final_amount,
        }))
        await self._ws.broadcast_to_passenger(
            ride.passenger_id, PassengerEvent.RIDE_COMPLETED,
            {"ride_id": str(ride.id), "final_price": final_amount},
        )
        return _ride_to_resp(ride)

    def _ensure_driver_is_at_dropoff(
        self,
        ride: ServiceRequest,
        cmd: VerifyAndCompleteRequest,
    ) -> None:
        dropoff = ride.dropoff_stop
        if dropoff is None:
            raise RideCompletionLocationError("Ride has no dropoff destination.")
        if cmd.driver_latitude is None or cmd.driver_longitude is None:
            raise RideCompletionLocationError(
                "Driver location is required to complete this ride."
            )

        distance_meters = _distance_meters(
            cmd.driver_latitude,
            cmd.driver_longitude,
            dropoff.latitude,
            dropoff.longitude,
        )
        if distance_meters > _COMPLETE_DESTINATION_RADIUS_METERS:
            raise RideCompletionLocationError(
                "Driver must be within "
                f"{_COMPLETE_DESTINATION_RADIUS_METERS:.0f}m of dropoff to complete this ride."
            )


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

    async def execute(self, ride_id: UUID, cmd: AddStopRequest, passenger_id: UUID) -> StopResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        if ride.passenger_id != passenger_id:
            raise UnauthorisedRideAccessError(
                "Only the passenger who created this ride may add stops."
            )
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
        if stop.arrived_at is None:
            raise StopNotFoundError(f"Stop {stop_id} arrival timestamp was not set.")
        await self._stop_repo.update_arrived_at(stop_id, stop.arrived_at)
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
        if stop.completed_at is None:
            raise StopNotFoundError(f"Stop {stop_id} completion timestamp was not set.")
        await self._stop_repo.update_completed_at(stop_id, stop.completed_at)
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

    async def execute(
        self,
        ride_id: UUID,
        cmd: UploadProofRequest,
        uploader_user_id: UUID | None = None,
        uploader_driver_id: UUID | None = None,
    ) -> ProofImageResponse:
        ride = await _load_ride_or_404(self._repo, ride_id)
        # Authorise: only the passenger or the assigned driver may register proofs
        if uploader_user_id is not None:
            if ride.passenger_id != uploader_user_id:
                raise UnauthorisedRideAccessError(
                    "Only the ride passenger may upload proof as a user."
                )
        elif uploader_driver_id is not None:
            if ride.assigned_driver_id != uploader_driver_id:
                raise UnauthorisedRideAccessError(
                    "Only the assigned driver may upload proof for this ride."
                )
        else:
            raise UnauthorisedRideAccessError("Authenticated principal required to upload proof.")
        proof = ProofImage.create(
            service_request_id=ride_id,
            proof_type=cmd.proof_type,
            file_key=cmd.file_key,
            # Derive uploader fields from the validated principal, not the request body
            uploaded_by_user_id=uploader_user_id,
            uploaded_by_driver_id=uploader_driver_id,
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
        storage: S3StorageProvider,
    ) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(
        self,
        ride_id: UUID,
        cmd: ProofUploadUrlRequest,
        actor_user_id: UUID,
    ) -> ProofUploadUrlResponse:
        from ..infrastructure.storage import build_proof_key

        ride = await _load_ride_or_404(self._repo, ride_id)
        # Authorise: only the passenger or the assigned driver may request a presigned URL
        is_passenger = ride.passenger_id == actor_user_id
        is_driver = (
            ride.assigned_driver_id is not None
            # actor_user_id here is already the resolved driver_id when caller is a driver;
            # the router passes the resolved driver_id for driver callers.
            and ride.assigned_driver_id == actor_user_id
        )
        if not (is_passenger or is_driver):
            raise UnauthorisedRideAccessError(
                "Only the ride passenger or assigned driver may generate a proof upload URL."
            )

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
        storage: S3StorageProvider,
    ) -> None:
        self._proof_repo = proof_repo
        self._storage = storage

    async def execute(
        self,
        ride_id: UUID,
        proof_id: UUID,
        actor_user_id: UUID,
    ) -> ProofImageWithUrlResponse:
        from ..domain.exceptions import RideNotFoundError, UnauthorisedRideAccessError

        proofs = await self._proof_repo.find_by_ride(ride_id)
        proof = next((p for p in proofs if p.id == proof_id), None)
        if proof is None:
            raise RideNotFoundError(f"Proof {proof_id} not found on ride {ride_id}.")

        # Authorise: verify the actor is either the uploader or matches ride ownership
        # (proof carries either uploaded_by_user_id or uploaded_by_driver_id)
        caller_is_uploader = (
            proof.uploaded_by_user_id == actor_user_id
            or proof.uploaded_by_driver_id == actor_user_id
        )
        if not caller_is_uploader:
            raise UnauthorisedRideAccessError(
                "Only the uploader of this proof may retrieve its presigned URL."
            )

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
