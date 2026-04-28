"""Concrete SQLAlchemy 2.0 repositories for the ride service.

Each repository operates on an injected AsyncSession. Transaction
boundaries are owned by the FastAPI dependency (get_async_session):
it commits on success and rolls back on any exception.

ORM field mapping reminders
----------------------------
ServiceRequestORM.user_id          ← ServiceRequest.passenger_id
ServiceRequestORM.assigned_driver_id ← ServiceRequest.assigned_driver_id
RequestStatus.MATCHING              ← RideStatus.MATCHING  (BIDDING is legacy)
allowed_fuel_types                  ← not a mapped column; skipped on persist
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

import sqlalchemy
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..domain.models import (
    PricingMode,
    ProofImage,
    ProofType,
    RideStatus,
    ServiceCategory,
    ServiceRequest,
    ServiceType,
    Stop,
    StopType,
    VerificationCode,
)
from .orm_models import (
    CityRideDetailORM,
    CourierDetailORM,
    FreightDetailORM,
    GroceryDetailORM,
    IntercityDetailORM,
    IntercityPassengerGroupORM,
    RequestStatus,
    ServiceProofImageORM,
    ServiceRequestORM,
    ServiceStopORM,
    ServiceVerificationCodeORM,
)

logger = logging.getLogger("ride.repositories")

# Map domain RideStatus → ORM RequestStatus
_STATUS_TO_ORM: dict[RideStatus, RequestStatus] = {
    RideStatus.CREATED:     RequestStatus.CREATED,
    RideStatus.MATCHING:    RequestStatus.MATCHING,
    RideStatus.ACCEPTED:    RequestStatus.ACCEPTED,
    RideStatus.ARRIVING:    RequestStatus.ARRIVING,
    RideStatus.IN_PROGRESS: RequestStatus.IN_PROGRESS,
    RideStatus.COMPLETED:   RequestStatus.COMPLETED,
    RideStatus.CANCELLED:   RequestStatus.CANCELLED,
}

# Map ORM RequestStatus → domain RideStatus (BIDDING treated as MATCHING)
_STATUS_FROM_ORM: dict[RequestStatus, RideStatus] = {
    RequestStatus.CREATED:     RideStatus.CREATED,
    RequestStatus.BIDDING:     RideStatus.MATCHING,   # legacy value
    RequestStatus.MATCHING:    RideStatus.MATCHING,
    RequestStatus.ACCEPTED:    RideStatus.ACCEPTED,
    RequestStatus.ARRIVING:    RideStatus.ARRIVING,
    RequestStatus.IN_PROGRESS: RideStatus.IN_PROGRESS,
    RequestStatus.COMPLETED:   RideStatus.COMPLETED,
    RequestStatus.CANCELLED:   RideStatus.CANCELLED,
}


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

def _stop_orm_to_domain(o: ServiceStopORM) -> Stop:
    return Stop(
        id=o.id,
        service_request_id=o.service_request_id,
        sequence_order=o.sequence_order,
        stop_type=StopType(o.stop_type.value),
        latitude=float(o.latitude),
        longitude=float(o.longitude),
        place_name=o.place_name,
        address_line_1=o.address_line_1,
        address_line_2=o.address_line_2,
        city=o.city,
        state=o.state,
        country=o.country,
        postal_code=o.postal_code,
        contact_name=o.contact_name,
        contact_phone=o.contact_phone,
        instructions=o.instructions,
        arrived_at=o.arrived_at,
        completed_at=o.completed_at,
    )


def _stop_domain_to_orm(stop: Stop) -> ServiceStopORM:
    from .orm_models import StopType as OrmStopType
    return ServiceStopORM(
        id=stop.id,
        service_request_id=stop.service_request_id,
        sequence_order=stop.sequence_order,
        stop_type=OrmStopType(stop.stop_type.value),
        latitude=stop.latitude,
        longitude=stop.longitude,
        place_name=stop.place_name,
        address_line_1=stop.address_line_1,
        address_line_2=stop.address_line_2,
        city=stop.city,
        state=stop.state,
        country=stop.country,
        postal_code=stop.postal_code,
        contact_name=stop.contact_name,
        contact_phone=stop.contact_phone,
        instructions=stop.instructions,
    )


def _proof_orm_to_domain(o: ServiceProofImageORM) -> ProofImage:
    return ProofImage(
        id=o.id,
        service_request_id=o.service_request_id,
        stop_id=o.stop_id,
        proof_type=ProofType(o.proof_type.value),
        file_key=o.file_key,
        file_name=o.file_name,
        mime_type=o.mime_type,
        file_size_bytes=o.file_size_bytes,
        checksum_sha256=o.checksum_sha256,
        is_primary=o.is_primary,
        uploaded_by_user_id=o.uploaded_by_user_id,
        uploaded_by_driver_id=o.uploaded_by_driver_id,
        uploaded_at=o.uploaded_at,
    )


def _code_orm_to_domain(o: ServiceVerificationCodeORM) -> VerificationCode:
    return VerificationCode(
        id=o.id,
        service_request_id=o.service_request_id,
        stop_id=o.stop_id,
        code=o.code,
        is_verified=o.is_verified,
        attempts=o.attempts,
        max_attempts=o.max_attempts,
        expires_at=o.expires_at,
        generated_at=o.generated_at,
        verified_at=o.verified_at,
        verified_by_user_id=o.verified_by_user_id,
        verified_by_driver_id=o.verified_by_driver_id,
    )


def _ride_orm_to_domain(o: ServiceRequestORM) -> ServiceRequest:
    return ServiceRequest(
        id=o.id,
        passenger_id=o.user_id,
        service_type=ServiceType(o.service_type.value),
        category=ServiceCategory(o.category.value),
        pricing_mode=PricingMode(o.pricing_mode.value),
        status=_STATUS_FROM_ORM[o.status],
        assigned_driver_id=o.assigned_driver_id,
        baseline_min_price=float(o.baseline_min_price) if o.baseline_min_price is not None else None,
        baseline_max_price=float(o.baseline_max_price) if o.baseline_max_price is not None else None,
        final_price=float(o.final_price) if o.final_price is not None else None,
        scheduled_at=o.scheduled_at,
        is_scheduled=o.is_scheduled,
        is_risky=o.is_risky,
        auto_accept_driver=o.auto_accept_driver,
        requires_otp_start=getattr(o.city_ride, "requires_otp_start", False) if "city_ride" not in sqlalchemy.inspect(o).unloaded and o.city_ride else False,
        requires_otp_end=getattr(o.city_ride, "requires_otp_end", False) if "city_ride" not in sqlalchemy.inspect(o).unloaded and o.city_ride else False,
        accepted_at=o.accepted_at,
        completed_at=o.completed_at,
        cancelled_at=o.cancelled_at,
        cancellation_reason=o.cancellation_reason,
        created_at=o.created_at,
        stops=[_stop_orm_to_domain(s) for s in o.stops] if "stops" not in sqlalchemy.inspect(o).unloaded and o.stops else [],
        proof_images=[_proof_orm_to_domain(p) for p in o.proof_images] if "proof_images" not in sqlalchemy.inspect(o).unloaded and o.proof_images else [],
        verification_codes=[_code_orm_to_domain(c) for c in o.verification_codes] if "verification_codes" not in sqlalchemy.inspect(o).unloaded and o.verification_codes else [],
    )


def _build_detail_orm(
    ride_id: UUID,
    service_type: ServiceType,
    detail: dict[str, Any],
) -> Any:
    """Construct the correct detail ORM object from a dict payload."""
    from .orm_models import (
        DriverGenderPreference as OrmDriverGenderPref,
    )
    from .orm_models import (
        VehicleType as OrmVehicleType,
    )

    if service_type == ServiceType.CITY_RIDE:
        return CityRideDetailORM(
            service_request_id=ride_id,
            passenger_count=detail.get("passenger_count", 1),
            is_ac=detail.get("is_ac", False),
            preferred_vehicle_type=(
                OrmVehicleType(detail["preferred_vehicle_type"])
                if detail.get("preferred_vehicle_type") else None
            ),
            driver_gender_preference=OrmDriverGenderPref(
                detail.get("driver_gender_preference", "NO_PREFERENCE")
            ),
            is_shared_ride=detail.get("is_shared_ride", False),
            max_co_passengers=detail.get("max_co_passengers"),
            is_smoking_allowed=detail.get("is_smoking_allowed", False),
            is_pet_allowed=detail.get("is_pet_allowed", False),
            requires_wheelchair_access=detail.get("requires_wheelchair_access", False),
            max_wait_time_minutes=detail.get("max_wait_time_minutes"),
            requires_otp_start=detail.get("requires_otp_start", True),
            requires_otp_end=detail.get("requires_otp_end", True),
            estimated_price=detail.get("estimated_price"),
            surge_multiplier_applied=detail.get("surge_multiplier_applied"),
        )

    if service_type == ServiceType.INTERCITY:
        orm = IntercityDetailORM(
            service_request_id=ride_id,
            passenger_count=detail["passenger_count"],
            luggage_count=detail.get("luggage_count", 0),
            child_count=detail.get("child_count", 0),
            senior_count=detail.get("senior_count", 0),
            preferred_departure_time=detail.get("preferred_departure_time"),
            departure_time_flexibility_minutes=detail.get("departure_time_flexibility_minutes"),
            is_round_trip=detail.get("is_round_trip", False),
            return_time=detail.get("return_time"),
            trip_distance_km=detail.get("trip_distance_km"),
            estimated_duration_minutes=detail.get("estimated_duration_minutes"),
            route_polyline=detail.get("route_polyline"),
            vehicle_type_requested=(
                OrmVehicleType(detail["vehicle_type_requested"])
                if detail.get("vehicle_type_requested") else None
            ),
            min_vehicle_capacity=detail.get("min_vehicle_capacity"),
            requires_luggage_carrier=detail.get("requires_luggage_carrier", False),
            estimated_price=detail.get("estimated_price"),
            price_per_km=detail.get("price_per_km"),
            toll_estimate=detail.get("toll_estimate"),
            fuel_surcharge=detail.get("fuel_surcharge"),
            total_stops=detail.get("total_stops", 0),
            is_multi_city_trip=detail.get("is_multi_city_trip", False),
            requires_identity_verification=detail.get("requires_identity_verification", False),
            emergency_contact_name=detail.get("emergency_contact_name"),
            emergency_contact_number=detail.get("emergency_contact_number"),
            matching_priority_score=detail.get("matching_priority_score"),
            demand_zone_id=detail.get("demand_zone_id"),
        )
        # Add passenger groups if present
        for grp in detail.get("passenger_groups", []):
            orm.passenger_groups.append(
                IntercityPassengerGroupORM(
                    service_request_id=ride_id,
                    intercity_service_request_id=ride_id,
                    passenger_count=grp["passenger_count"],
                    luggage_count=grp.get("luggage_count", 0),
                    full_name=grp.get("full_name"),
                    phone_number=grp.get("phone_number"),
                    seat_preference=grp.get("seat_preference"),
                    special_needs=grp.get("special_needs"),
                )
            )
        return orm

    if service_type == ServiceType.FREIGHT:
        return FreightDetailORM(
            service_request_id=ride_id,
            cargo_weight=detail["cargo_weight"],
            cargo_type=detail["cargo_type"],
            requires_loader=detail.get("requires_loader", False),
            vehicle_type=OrmVehicleType(detail["vehicle_type"]),
            is_fragile=detail.get("is_fragile", False),
            requires_temperature_control=detail.get("requires_temperature_control", False),
            declared_value=detail.get("declared_value"),
            commodity_notes=detail.get("commodity_notes"),
            estimated_load_hours=detail.get("estimated_load_hours"),
        )

    if service_type == ServiceType.COURIER:
        return CourierDetailORM(
            service_request_id=ride_id,
            item_description=detail["item_description"],
            item_weight=detail.get("item_weight"),
            total_parcels=detail.get("total_parcels", 1),
            recipient_name=detail["recipient_name"],
            recipient_phone=detail["recipient_phone"],
            recipient_email=detail.get("recipient_email"),
            is_fragile=detail.get("is_fragile", False),
            requires_signature=detail.get("requires_signature", False),
            declared_value=detail.get("declared_value"),
            special_handling_notes=detail.get("special_handling_notes"),
        )

    if service_type == ServiceType.GROCERY:
        return GroceryDetailORM(
            service_request_id=ride_id,
            store_id=detail["store_id"],
            total_items=detail.get("total_items", 0),
            special_notes=detail.get("special_notes"),
            contactless_delivery=detail.get("contactless_delivery", False),
            estimated_bag_count=detail.get("estimated_bag_count"),
        )

    raise ValueError(f"Unknown service_type: {service_type}")


# ---------------------------------------------------------------------------
# ServiceRequest repository
# ---------------------------------------------------------------------------

class ServiceRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_full(
        self,
        ride: ServiceRequest,
        stops: list[Stop],
        detail_data: dict[str, Any],
    ) -> ServiceRequest:
        """Atomically persist ride + detail + stops in one flush."""
        from .orm_models import PricingMode as OrmPricingMode
        from .orm_models import ServiceCategory as OrmCategory
        from .orm_models import ServiceType as OrmServiceType

        ride_orm = ServiceRequestORM(
            id=ride.id,
            user_id=ride.passenger_id,
            assigned_driver_id=ride.assigned_driver_id,
            service_type=OrmServiceType(ride.service_type.value),
            category=OrmCategory(ride.category.value),
            pricing_mode=OrmPricingMode(ride.pricing_mode.value),
            status=_STATUS_TO_ORM[ride.status],
            baseline_min_price=ride.baseline_min_price,
            baseline_max_price=ride.baseline_max_price,
            auto_accept_driver=ride.auto_accept_driver,
            final_price=ride.final_price,
            scheduled_at=ride.scheduled_at,
            is_scheduled=ride.is_scheduled,
            is_risky=ride.is_risky,
        )
        self._session.add(ride_orm)

        detail_orm = _build_detail_orm(ride.id, ride.service_type, detail_data)
        self._session.add(detail_orm)

        for stop in stops:
            self._session.add(_stop_domain_to_orm(stop))

        await self._session.flush()
        logger.info("Ride created ride_id=%s service_type=%s", ride.id, ride.service_type.value)
        ride.stops = stops
        return ride

    async def find_by_id(
        self,
        ride_id: UUID,
        *,
        load_relations: bool = True,
    ) -> ServiceRequest | None:
        opts = []
        if load_relations:
            opts = [
                selectinload(ServiceRequestORM.stops),
                selectinload(ServiceRequestORM.proof_images),
                selectinload(ServiceRequestORM.verification_codes),
                selectinload(ServiceRequestORM.city_ride),
                selectinload(ServiceRequestORM.intercity).selectinload(
                    IntercityDetailORM.passenger_groups
                ),
                selectinload(ServiceRequestORM.freight),
                selectinload(ServiceRequestORM.courier),
                selectinload(ServiceRequestORM.grocery),
            ]
        stmt = select(ServiceRequestORM).where(ServiceRequestORM.id == ride_id)
        for o in opts:
            stmt = stmt.options(o)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _ride_orm_to_domain(orm) if orm else None

    async def find_by_passenger(
        self,
        passenger_id: UUID,
        *,
        status_filter: list[RideStatus] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ServiceRequest]:
        stmt = (
            select(ServiceRequestORM)
            .where(ServiceRequestORM.user_id == passenger_id)
            .options(selectinload(ServiceRequestORM.stops))
            .order_by(ServiceRequestORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status_filter:
            orm_statuses = [_STATUS_TO_ORM[s] for s in status_filter]
            stmt = stmt.where(ServiceRequestORM.status.in_(orm_statuses))
        result = await self._session.execute(stmt)
        return [_ride_orm_to_domain(o) for o in result.scalars().all()]

    async def update_status(
        self,
        ride_id: UUID,
        status: RideStatus,
        *,
        accepted_at: datetime | None = None,
        completed_at: datetime | None = None,
        cancelled_at: datetime | None = None,
        cancellation_reason: str | None = None,
        assigned_driver_id: UUID | None = None,
        final_price: float | None = None,
    ) -> None:
        values: dict[str, Any] = {"status": _STATUS_TO_ORM[status]}
        if accepted_at is not None:
            values["accepted_at"] = accepted_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if cancelled_at is not None:
            values["cancelled_at"] = cancelled_at
        if cancellation_reason is not None:
            values["cancellation_reason"] = cancellation_reason
        if assigned_driver_id is not None:
            values["assigned_driver_id"] = assigned_driver_id
        if final_price is not None:
            values["final_price"] = final_price

        await self._session.execute(
            update(ServiceRequestORM)
            .where(ServiceRequestORM.id == ride_id)
            .values(**values)
        )


# ---------------------------------------------------------------------------
# Stop repository
# ---------------------------------------------------------------------------

class StopRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, stop: Stop) -> Stop:
        orm = _stop_domain_to_orm(stop)
        self._session.add(orm)
        await self._session.flush()
        return stop

    async def find_by_id(self, stop_id: UUID) -> Stop | None:
        result = await self._session.execute(
            select(ServiceStopORM).where(ServiceStopORM.id == stop_id)
        )
        orm = result.scalar_one_or_none()
        return _stop_orm_to_domain(orm) if orm else None

    async def find_by_ride(self, ride_id: UUID) -> list[Stop]:
        result = await self._session.execute(
            select(ServiceStopORM)
            .where(ServiceStopORM.service_request_id == ride_id)
            .order_by(ServiceStopORM.sequence_order)
        )
        return [_stop_orm_to_domain(o) for o in result.scalars().all()]

    async def update_arrived_at(self, stop_id: UUID, arrived_at: datetime) -> None:
        await self._session.execute(
            update(ServiceStopORM)
            .where(ServiceStopORM.id == stop_id)
            .values(arrived_at=arrived_at)
        )

    async def update_completed_at(self, stop_id: UUID, completed_at: datetime) -> None:
        await self._session.execute(
            update(ServiceStopORM)
            .where(ServiceStopORM.id == stop_id)
            .values(completed_at=completed_at)
        )


# ---------------------------------------------------------------------------
# ProofImage repository
# ---------------------------------------------------------------------------

class ProofImageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, proof: ProofImage) -> ProofImage:
        from .orm_models import ProofType as OrmProofType
        orm = ServiceProofImageORM(
            id=proof.id,
            service_request_id=proof.service_request_id,
            stop_id=proof.stop_id,
            proof_type=OrmProofType(proof.proof_type.value),
            file_key=proof.file_key,
            file_name=proof.file_name,
            mime_type=proof.mime_type,
            file_size_bytes=proof.file_size_bytes,
            checksum_sha256=proof.checksum_sha256,
            is_primary=proof.is_primary,
            uploaded_by_user_id=proof.uploaded_by_user_id,
            uploaded_by_driver_id=proof.uploaded_by_driver_id,
        )
        self._session.add(orm)
        await self._session.flush()
        return proof

    async def find_by_ride(self, ride_id: UUID) -> list[ProofImage]:
        result = await self._session.execute(
            select(ServiceProofImageORM)
            .where(ServiceProofImageORM.service_request_id == ride_id)
            .order_by(ServiceProofImageORM.uploaded_at)
        )
        return [_proof_orm_to_domain(o) for o in result.scalars().all()]

    async def find_by_stop(self, stop_id: UUID) -> list[ProofImage]:
        result = await self._session.execute(
            select(ServiceProofImageORM)
            .where(ServiceProofImageORM.stop_id == stop_id)
        )
        return [_proof_orm_to_domain(o) for o in result.scalars().all()]


# ---------------------------------------------------------------------------
# VerificationCode repository
# ---------------------------------------------------------------------------

class VerificationCodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, code: VerificationCode) -> VerificationCode:
        orm = ServiceVerificationCodeORM(
            id=code.id,
            service_request_id=code.service_request_id,
            stop_id=code.stop_id,
            code=code.code,
            is_verified=code.is_verified,
            attempts=code.attempts,
            max_attempts=code.max_attempts,
            expires_at=code.expires_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return code

    async def find_active_by_ride(
        self,
        ride_id: UUID,
        stop_id: UUID | None = None,
    ) -> VerificationCode | None:
        stmt = (
            select(ServiceVerificationCodeORM)
            .where(
                ServiceVerificationCodeORM.service_request_id == ride_id,
                ServiceVerificationCodeORM.is_verified.is_(False),
            )
            .order_by(ServiceVerificationCodeORM.generated_at.desc())
            .limit(1)
        )
        if stop_id is not None:
            stmt = stmt.where(ServiceVerificationCodeORM.stop_id == stop_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _code_orm_to_domain(orm) if orm else None

    async def update_verification(self, code: VerificationCode) -> None:
        await self._session.execute(
            update(ServiceVerificationCodeORM)
            .where(ServiceVerificationCodeORM.id == code.id)
            .values(
                attempts=code.attempts,
                is_verified=code.is_verified,
                verified_at=code.verified_at,
                verified_by_user_id=code.verified_by_user_id,
                verified_by_driver_id=code.verified_by_driver_id,
            )
        )
