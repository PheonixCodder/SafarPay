"""Location Service API router — HTTP endpoints + WebSocket endpoints.

WebSocket Auth Note (Intentional Project-Wide Exception):
  All WebSocket endpoints use `?token=<JWT>` query parameter authentication.
  This is an intentional, documented exception to the platform security policy
  (security/dependencies.py) because mobile WebSocket clients (iOS/Android)
  cannot set Authorization headers on the HTTP upgrade handshake.
  HTTP endpoints continue to use Authorization: Bearer <token> exclusively.

Endpoints:
  HTTP:
    POST   /drivers/{driver_id}/location      — HTTP fallback GPS update
    GET    /drivers/{driver_id}/location      — current driver location
    POST   /drivers/{driver_id}/status        — go ONLINE / OFFLINE
    GET    /drivers/nearby                    — nearby ONLINE drivers (Geospatial only)
    GET    /rides/{ride_id}/locations         — driver + passenger live position
    GET    /actors/{actor_id}/history         — PostGIS history (admin)
    POST   /geocode                           — Mapbox forward geocode
    POST   /reverse                           — Mapbox reverse geocode

  WebSocket:
    WS /ws/drivers/location                   — driver GPS ping stream
    WS /ws/rides/{ride_id}/track              — passenger ride tracking subscription
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sp.core.config import get_settings
from sp.infrastructure.db.session import get_async_session
from sp.infrastructure.security.dependencies import (
    CurrentDriver,
    CurrentUser,
    OptionalDriverId,
    get_current_driver_ws,
)
from sp.infrastructure.security.jwt import verify_token
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.schemas import (
    AddressResponse,
    DriverLocationResponse,
    DriverStatusRequest,
    GeocodeRequest,
    LocationHistoryResponse,
    LocationUpdateRequest,
    NearbyDriversResponse,
    ReverseGeocodeRequest,
    RideLocationsResponse,
    StatusResponse,
)
from ..application.use_cases import (
    GeocodeUseCase,
    GetCurrentDriverLocationUseCase,
    GetLocationHistoryUseCase,
    GetNearbyDriversUseCase,
    GetRideLocationsUseCase,
    ReverseGeocodeUseCase,
    SetDriverStatusUseCase,
    UpdateDriverLocationUseCase,
)
from ..domain.exceptions import (
    ActorNotFoundError,
    GPSAccuracyTooLowError,
    ImpossibleJumpError,
    InvalidCoordinatesError,
    LocationDomainError,
    RateLimitExceededError,
    SpeedValidationError,
    StaleLocationError,
    UnauthorisedLocationAccessError,
)
from ..infrastructure.dependencies import (
    get_current_driver_location_uc,
    get_geocode_uc,
    get_location_history_uc,
    get_nearby_drivers_uc,
    get_reverse_geocode_uc,
    get_ride_locations_uc,
    get_set_driver_status_uc,
    get_update_driver_location_uc,
    get_ws_manager,
)
from ..infrastructure.websocket_manager import WebSocketManager

logger = logging.getLogger("location.router")
router = APIRouter(tags=["location"])


# ---------------------------------------------------------------------------
# Domain exception → HTTP response dispatcher
# ---------------------------------------------------------------------------

def _handle_domain(exc: LocationDomainError) -> HTTPException:
    mapping = {
        InvalidCoordinatesError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        GPSAccuracyTooLowError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        SpeedValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ImpossibleJumpError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ActorNotFoundError: status.HTTP_404_NOT_FOUND,
        StaleLocationError: status.HTTP_404_NOT_FOUND,
        UnauthorisedLocationAccessError: status.HTTP_403_FORBIDDEN,
        RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    }
    code = mapping.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return HTTPException(status_code=code, detail=str(exc))


# ---------------------------------------------------------------------------
# HTTP — Driver location
# ---------------------------------------------------------------------------

@router.post(
    "/drivers/{driver_id}/location",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="HTTP fallback GPS update for drivers",
)
async def update_driver_location_http(
    driver_id: UUID,
    req: LocationUpdateRequest,
    current_driver: CurrentDriver,
    current_user: CurrentUser,
    uc: Annotated[UpdateDriverLocationUseCase, Depends(get_update_driver_location_uc)],
) -> None:
    """HTTP fallback for when the driver WebSocket is unavailable."""
    if str(current_driver) != str(driver_id) and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        await uc.execute(driver_id=driver_id, req=req)
    except LocationDomainError as exc:
        raise _handle_domain(exc) from exc


@router.get(
    "/drivers/{driver_id}/location",
    response_model=DriverLocationResponse,
    summary="Get current driver location",
)
async def get_driver_location(
    current_driver: CurrentDriver,
    uc: Annotated[GetCurrentDriverLocationUseCase, Depends(get_current_driver_location_uc)],
) -> DriverLocationResponse:
    try:
        return await uc.execute(current_driver)
    except LocationDomainError as exc:
        raise _handle_domain(exc) from exc


@router.post(
    "/drivers/{driver_id}/status",
    response_model=StatusResponse,
    summary="Set driver ONLINE or OFFLINE",
)
async def set_driver_status(
    driver_id: UUID,
    current_driver: CurrentDriver,
    current_user: CurrentUser,
    req: DriverStatusRequest,
    uc: Annotated[SetDriverStatusUseCase, Depends(get_set_driver_status_uc)],
) -> StatusResponse:
    if str(current_driver) != str(driver_id) and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return await uc.execute(driver_id=driver_id, req=req)
    except LocationDomainError as exc:
        raise _handle_domain(exc) from exc


# ---------------------------------------------------------------------------
# HTTP — Nearby drivers (Geospatial Service internal endpoint)
# ---------------------------------------------------------------------------

@router.get(
    "/drivers/nearby",
    response_model=NearbyDriversResponse,
    summary="[Internal] Nearby ONLINE drivers — Geospatial Service only",
)
async def get_nearby_drivers(
    current_user: CurrentUser,
    uc: Annotated[GetNearbyDriversUseCase, Depends(get_nearby_drivers_uc)],
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=5.0, gt=0, le=50),
    max_results: int = Query(default=50, gt=0, le=200),
) -> NearbyDriversResponse:
    return await uc.execute(
        latitude=lat,
        longitude=lng,
        radius_km=radius_km,
        max_results=max_results,
    )


# ---------------------------------------------------------------------------
# HTTP — Ride live locations
# ---------------------------------------------------------------------------

@router.get(
    "/rides/{ride_id}/locations",
    response_model=RideLocationsResponse,
    summary="Driver + passenger live positions for an active ride",
)
async def get_ride_locations(
    ride_id: UUID,
    current_user: CurrentUser,
    current_driver_id: OptionalDriverId,
    uc: Annotated[GetRideLocationsUseCase, Depends(get_ride_locations_uc)],
) -> RideLocationsResponse:
    """Returns both participant locations. Auth is verified against Redis participant cache —
    no caller-supplied driver_id/passenger_user_id params needed or accepted."""
    try:
        return await uc.execute(
            ride_id=ride_id,
            caller_user_id=current_user.user_id,
            caller_driver_id=current_driver_id,
        )
    except LocationDomainError as exc:
        raise _handle_domain(exc) from exc


# ---------------------------------------------------------------------------
# HTTP — Location history (admin)
# ---------------------------------------------------------------------------

@router.get(
    "/actors/{actor_id}/history",
    response_model=LocationHistoryResponse,
    summary="[Admin] Location history from PostGIS",
)
async def get_location_history(
    actor_id: UUID,
    current_user: CurrentUser,
    uc: Annotated[GetLocationHistoryUseCase, Depends(get_location_history_uc)],
    since: Annotated[datetime, Query(...)],
    until: Annotated[datetime, Query(...)],
    actor_type: Annotated[str, Query(pattern="^(DRIVER|PASSENGER)$")] = "DRIVER",
) -> LocationHistoryResponse:
    try:
        return await uc.execute(
            actor_id=actor_id,
            actor_type_str=actor_type,
            since=since,
            until=until,
            caller_role=current_user.role,
        )
    except LocationDomainError as exc:
        raise _handle_domain(exc) from exc


# ---------------------------------------------------------------------------
# HTTP — Geocoding (preserved)
# ---------------------------------------------------------------------------

@router.post("/geocode", response_model=AddressResponse, summary="Mapbox forward geocode")
async def geocode(
    req: GeocodeRequest,
    current_user: CurrentUser,
    uc: Annotated[GeocodeUseCase, Depends(get_geocode_uc)],
) -> AddressResponse:
    return await uc.execute(req.address)


@router.post("/reverse", response_model=AddressResponse, summary="Mapbox reverse geocode")
async def reverse_geocode(
    req: ReverseGeocodeRequest,
    current_user: CurrentUser,
    uc: Annotated[ReverseGeocodeUseCase, Depends(get_reverse_geocode_uc)],
) -> AddressResponse:
    return await uc.execute(req.latitude, req.longitude)


# ---------------------------------------------------------------------------
# WebSocket — Driver GPS stream
# ---------------------------------------------------------------------------

@router.websocket("/ws/drivers/location")
async def ws_driver_location(
    websocket: WebSocket,
    current_driver: Annotated[UUID, Depends(get_current_driver_ws)],
    ws_manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    uc: Annotated[UpdateDriverLocationUseCase, Depends(get_update_driver_location_uc)],
    set_status_uc: Annotated[SetDriverStatusUseCase, Depends(get_set_driver_status_uc)],
) -> None:
    """Driver connects, sends GPS pings every ~5 seconds.

    WS message format (client → server):
      {"lat": 31.52, "lng": 74.35, "accuracy": 8.5, "speed": 42.1, "heading": 180, "ts": 1714300000000}

    Heartbeat: server sends {"event": "ping"} every 30s if no message is received.
    Client must reply with {"event": "pong"} within 10s or the connection is closed (code 1001).

    On disconnect: driver is marked OFFLINE and removed from Redis Geo set.
    """
    driver_id = current_driver
    await ws_manager.connect_driver(driver_id, websocket)
    logger.info("driver=%s | WS connected", driver_id)

    try:
        while True:
            # Server-side heartbeat: wait 30s for a message; if nothing arrives,
            # send a server ping and wait up to 10s for pong before closing.
            try:
                raw = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
            except asyncio.TimeoutError:
                # Idle for 30s — probe the connection
                await websocket.send_json({"event": "ping"})
                try:
                    pong = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
                    if pong.get("event") != "pong":
                        logger.warning("driver=%s | No pong received, closing WS", driver_id)
                        await websocket.close(code=1001, reason="Heartbeat timeout")
                        return
                    continue
                except asyncio.TimeoutError:
                    logger.warning("driver=%s | Heartbeat timeout, closing WS", driver_id)
                    await websocket.close(code=1001, reason="Heartbeat timeout")
                    return

            data = raw

            # Handle client-initiated ping-pong
            if data.get("event") == "ping":
                await websocket.send_json({"event": "pong"})
                continue
            if data.get("event") == "pong":
                continue

            try:
                req = LocationUpdateRequest(**data)
                ride_id_str = data.get("ride_id")
                ride_id = UUID(ride_id_str) if ride_id_str else None
                await uc.execute(driver_id=driver_id, req=req, ride_id=ride_id)
            except pydantic.ValidationError as exc:
                logger.warning("driver=%s | Malformed WS message: %s", driver_id, exc)
                await websocket.send_json({"event": "error", "detail": "invalid_message_format"})
            except RateLimitExceededError:
                await websocket.send_json({"event": "error", "detail": "rate_limit_exceeded"})
            except (GPSAccuracyTooLowError, SpeedValidationError, ImpossibleJumpError) as exc:
                logger.warning("driver=%s | Ping discarded: %s", driver_id, exc)
                await websocket.send_json({"event": "error", "detail": "invalid_location"})
            except InvalidCoordinatesError as exc:
                logger.warning("driver=%s | Invalid coords: %s", driver_id, exc)
                await websocket.send_json({"event": "error", "detail": "invalid_coordinates"})
            except Exception as exc:  # noqa: BLE001
                logger.exception("driver=%s | Unexpected error processing ping: %s", driver_id, exc)

    except WebSocketDisconnect:
        logger.info("driver=%s | WS disconnected", driver_id)
    finally:
        await ws_manager.disconnect_driver(driver_id, websocket)
        if set_status_uc:
            from ..application.schemas import DriverStatusRequest
            await set_status_uc.execute(
                driver_id=driver_id,
                req=DriverStatusRequest(status="OFFLINE"),
            )


# ---------------------------------------------------------------------------
# WebSocket — Passenger ride tracking
# ---------------------------------------------------------------------------

@router.websocket("/ws/rides/{ride_id}/track")
async def ws_ride_track(
    websocket: WebSocket,
    ride_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    ws_manager: Annotated[WebSocketManager, Depends(get_ws_manager)],
    ride_locations_uc: Annotated[GetRideLocationsUseCase, Depends(get_ride_locations_uc)],
    token: Annotated[str, Query(description="JWT access token — intentional WS exception")],
) -> None:
    """Passenger subscribes to live driver location for a specific ride.

    The passenger receives DRIVER_LOCATION_UPDATED events pushed by the driver's
    GPS stream.  The connection is read-only from the passenger side (pong only).

    Heartbeat: server sends {"event": "ping"} every 30s if idle.
    Client must reply within 10s or the connection is closed (code 1001).

    WS message format (server → client):
      {"event": "DRIVER_LOCATION_UPDATED", "timestamp": "...",
       "data": {"driver_id": "...", "lat": 31.52, "lng": 74.35,
                "heading": 180, "speed": 42.1}}
    """
    settings = get_settings()
    payload = verify_token(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if not payload:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    user_id = payload.user_id
    result = await session.execute(
        text("SELECT id FROM verification.drivers WHERE user_id = :uid LIMIT 1"),
        {"uid": user_id},
    )
    row = result.fetchone()
    driver_id = row[0] if row else None

    # Authorization: verify caller is a participant of this ride
    # Reuses GetRideLocationsUseCase which reads from the Redis participant cache
    try:
        await ride_locations_uc.execute(
            ride_id=ride_id,
            caller_user_id=user_id,
            caller_driver_id=driver_id,
        )
    except UnauthorisedLocationAccessError:
        await websocket.close(code=1008, reason="Forbidden: not a ride participant")
        return
    except LocationDomainError:
        await websocket.close(code=1008, reason="Ride not accessible")
        return

    await ws_manager.connect_passenger(user_id, websocket)
    ws_manager.subscribe_ride(ride_id, user_id)
    logger.info("passenger=%s | Subscribed to ride=%s tracking", user_id, ride_id)

    try:
        while True:
            # Server-side heartbeat: wait 30s for any client message
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_text('{"event":"ping"}')
                try:
                    reply = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
                    if reply.strip() not in ('pong', '{"event":"pong"}'):
                        logger.warning("passenger=%s | No pong, closing ride=%s WS", user_id, ride_id)
                        await websocket.close(code=1001, reason="Heartbeat timeout")
                        return
                    continue
                except asyncio.TimeoutError:
                    logger.warning("passenger=%s | Heartbeat timeout on ride=%s", user_id, ride_id)
                    await websocket.close(code=1001, reason="Heartbeat timeout")
                    return

            # Handle client-initiated ping
            if msg.strip() in ("ping", '{"event":"ping"}'):
                await websocket.send_text('{"event":"pong"}')

    except WebSocketDisconnect:
        logger.info("passenger=%s | Disconnected from ride=%s tracking", user_id, ride_id)
    finally:
        ws_manager.unsubscribe_ride(ride_id, user_id)
        await ws_manager.disconnect_passenger(user_id, websocket)
