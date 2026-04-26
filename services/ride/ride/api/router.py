"""Ride service HTTP and WebSocket router.

Thin controllers only — validate, delegate to use case, map exceptions.
No business logic lives here.
"""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sp.core.observability.logging import get_logger
from sp.infrastructure.security.dependencies import CurrentUser

from ..application.schemas import (
    AcceptRideRequest,
    AddStopRequest,
    CancelRideRequest,
    CreateRideRequest,
    DriverCandidateResponse,
    GenerateVerificationCodeRequest,
    NearbyDriversResponse,
    ProofImageResponse,
    ProofImageWithUrlResponse,
    ProofUploadUrlRequest,
    ProofUploadUrlResponse,
    RideResponse,
    RideSummaryResponse,
    UploadProofRequest,
    VerificationCodeResponse,
    VerifyAndCompleteRequest,
    VerifyAndStartRequest,
    VerifyCodeRequest,
)
from ..application.use_cases import (
    AcceptRideUseCase,
    AddStopUseCase,
    BroadcastRideToDriversUseCase,
    CancelRideUseCase,
    CompleteRideUseCase,
    CreateRideUseCase,
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
)
from ..domain.exceptions import (
    InvalidStateTransitionError,
    ProofUploadError,
    RideAlreadyCancelledError,
    RideAlreadyCompletedError,
    RideNotFoundError,
    StopAlreadyCompletedError,
    StopNotArrivedError,
    StopNotFoundError,
    UnauthorisedRideAccessError,
    VerificationCodeAlreadyVerifiedError,
    VerificationCodeExpiredError,
    VerificationCodeExhaustedError,
    VerificationCodeInvalidError,
    VerificationCodeNotFoundError,
)
from ..domain.models import RideStatus
from ..infrastructure.dependencies import (
    get_accept_ride_uc,
    get_add_stop_uc,
    get_broadcast_uc,
    get_cancel_ride_uc,
    get_complete_ride_uc,
    get_create_ride_uc,
    get_gen_code_uc,
    get_gen_proof_url_uc,
    get_get_ride_uc,
    get_list_rides_uc,
    get_mark_arrived_uc,
    get_mark_completed_uc,
    get_nearby_drivers_uc,
    get_proof_with_url_uc,
    get_start_ride_uc,
    get_upload_proof_uc,
    get_verify_code_uc,
    get_ws_manager,
)
from ..infrastructure.websocket_manager import WebSocketManager

router = APIRouter(tags=["rides"])
logger = get_logger("ride.api")


# ---------------------------------------------------------------------------
# Exception → HTTP mapping
# ---------------------------------------------------------------------------

def _handle_domain(exc: Exception) -> HTTPException:
    mapping: dict[type, tuple[int, str]] = {
        RideNotFoundError:                      (404, str(exc)),
        StopNotFoundError:                      (404, str(exc)),
        VerificationCodeNotFoundError:          (404, str(exc)),
        UnauthorisedRideAccessError:            (403, str(exc)),
        InvalidStateTransitionError:            (409, str(exc)),
        RideAlreadyCancelledError:              (409, str(exc)),
        RideAlreadyCompletedError:              (409, str(exc)),
        StopAlreadyCompletedError:              (409, str(exc)),
        StopNotArrivedError:                    (409, str(exc)),
        VerificationCodeInvalidError:           (422, str(exc)),
        VerificationCodeExpiredError:           (422, str(exc)),
        VerificationCodeExhaustedError:         (429, str(exc)),
        VerificationCodeAlreadyVerifiedError:   (409, str(exc)),
        ProofUploadError:                       (422, str(exc)),
    }
    code, detail = mapping.get(type(exc), (500, "Internal server error"))
    return HTTPException(status_code=code, detail=detail)


# ---------------------------------------------------------------------------
# Rides — CRUD & lifecycle
# ---------------------------------------------------------------------------

@router.post("/rides", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    body: CreateRideRequest,
    current_user: CurrentUser,
    uc: Annotated[CreateRideUseCase, Depends(get_create_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(body, current_user.user_id)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.get("/rides", response_model=list[RideSummaryResponse])
async def list_rides(
    current_user: CurrentUser,
    uc: Annotated[ListPassengerRidesUseCase, Depends(get_list_rides_uc)],
    status_filter: list[RideStatus] | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[RideSummaryResponse]:
    return await uc.execute(current_user.user_id, status_filter=status_filter, limit=limit, offset=offset)


@router.get("/rides/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: UUID,
    uc: Annotated[GetRideUseCase, Depends(get_get_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id)
    except RideNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.post("/rides/{ride_id}/cancel", response_model=RideResponse)
async def cancel_ride(
    ride_id: UUID,
    body: CancelRideRequest,
    uc: Annotated[CancelRideUseCase, Depends(get_cancel_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/accept", response_model=RideResponse)
async def accept_ride(
    ride_id: UUID,
    body: AcceptRideRequest,
    uc: Annotated[AcceptRideUseCase, Depends(get_accept_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/start", response_model=RideResponse)
async def start_ride(
    ride_id: UUID,
    body: VerifyAndStartRequest,
    uc: Annotated[StartRideUseCase, Depends(get_start_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/complete", response_model=RideResponse)
async def complete_ride(
    ride_id: UUID,
    body: VerifyAndCompleteRequest,
    uc: Annotated[CompleteRideUseCase, Depends(get_complete_ride_uc)],
) -> RideResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Stops
# ---------------------------------------------------------------------------

@router.post("/rides/{ride_id}/stops", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_stop(
    ride_id: UUID,
    body: AddStopRequest,
    uc: Annotated[AddStopUseCase, Depends(get_add_stop_uc)],
) -> dict:
    try:
        stop = await uc.execute(ride_id, body)
        return stop.model_dump()
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/stops/{stop_id}/arrived", response_model=dict)
async def stop_arrived(
    stop_id: UUID,
    current_user: CurrentUser,
    uc: Annotated[MarkStopArrivedUseCase, Depends(get_mark_arrived_uc)],
) -> dict:
    try:
        stop = await uc.execute(stop_id, current_user.user_id)
        return stop.model_dump()
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/stops/{stop_id}/completed", response_model=dict)
async def stop_completed(
    stop_id: UUID,
    current_user: CurrentUser,
    uc: Annotated[MarkStopCompletedUseCase, Depends(get_mark_completed_uc)],
) -> dict:
    try:
        stop = await uc.execute(stop_id, current_user.user_id)
        return stop.model_dump()
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Verification codes
# ---------------------------------------------------------------------------

@router.post(
    "/rides/{ride_id}/verification-codes",
    response_model=VerificationCodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_verification_code(
    ride_id: UUID,
    body: GenerateVerificationCodeRequest,
    uc: Annotated[GenerateVerificationCodeUseCase, Depends(get_gen_code_uc)],
) -> VerificationCodeResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post("/rides/{ride_id}/verification-codes/verify", response_model=VerificationCodeResponse)
async def verify_code(
    ride_id: UUID,
    body: VerifyCodeRequest,
    uc: Annotated[VerifyVerificationCodeUseCase, Depends(get_verify_code_uc)],
) -> VerificationCodeResponse:
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


# ---------------------------------------------------------------------------
# Proofs
# ---------------------------------------------------------------------------

@router.post(
    "/rides/{ride_id}/proofs/upload-url",
    response_model=ProofUploadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate presigned S3 PUT URL for proof upload (step 1)",
    description=(
        "**3-step proof upload flow:**\n\n"
        "1. `POST /rides/{id}/proofs/upload-url` → receive `presigned_url` + `file_key`\n"
        "2. `PUT <presigned_url>` (client → S3, binary, matching `mime_type`)\n"
        "3. `POST /rides/{id}/proofs` → register metadata with `file_key`"
    ),
)
async def generate_proof_upload_url(
    ride_id: UUID,
    body: ProofUploadUrlRequest,
    current_user: CurrentUser,
    uc: Annotated[GenerateProofUploadUrlUseCase, Depends(get_gen_proof_url_uc)],
) -> ProofUploadUrlResponse:
    """Generate a time-limited presigned S3 PUT URL for a ride proof image."""
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.post(
    "/rides/{ride_id}/proofs",
    response_model=ProofImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register proof metadata after S3 upload (step 3)",
)
async def upload_proof(
    ride_id: UUID,
    body: UploadProofRequest,
    uc: Annotated[UploadProofUseCase, Depends(get_upload_proof_uc)],
) -> ProofImageResponse:
    """Register proof image metadata once the binary has been uploaded to S3."""
    try:
        return await uc.execute(ride_id, body)
    except Exception as exc:
        raise _handle_domain(exc) from None


@router.get(
    "/rides/{ride_id}/proofs/{proof_id}/url",
    response_model=ProofImageWithUrlResponse,
    summary="Get proof image record + presigned GET URL",
)
async def get_proof_url(
    ride_id: UUID,
    proof_id: UUID,
    current_user: CurrentUser,
    uc: Annotated[GetProofWithUrlUseCase, Depends(get_proof_with_url_uc)],
) -> ProofImageWithUrlResponse:
    """Return the proof metadata and a time-limited presigned GET URL for viewing."""
    try:
        return await uc.execute(ride_id, proof_id)
    except Exception as exc:
        raise _handle_domain(exc) from None



# ---------------------------------------------------------------------------
# Nearby drivers / matching
# ---------------------------------------------------------------------------

@router.get("/drivers/nearby", response_model=NearbyDriversResponse)
async def nearby_drivers(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: float = Query(default=5.0, ge=0.1, le=50.0),
    ride_id: UUID | None = Query(default=None),
    uc: FindNearbyDriversUseCase = Depends(get_nearby_drivers_uc),
) -> NearbyDriversResponse:
    return await uc.execute(lat, lng, radius, ride_id=ride_id)


# ---------------------------------------------------------------------------
# WebSocket — Drivers
# ---------------------------------------------------------------------------

@router.websocket("/ws/drivers")
async def ws_drivers(
    ws: WebSocket,
    driver_id: UUID,
    manager: WebSocketManager = Depends(get_ws_manager),
) -> None:
    """
    Driver real-time channel.
    Query param: driver_id (UUID of the authenticated driver).
    Receives: NEW_JOB, JOB_CANCELLED, JOB_ASSIGNED, JOB_UPDATED
    """
    await manager.connect_driver(driver_id, ws)
    try:
        while True:
            # Keep-alive: read any incoming pings from the client
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect_driver(driver_id, ws)
        logger.info("Driver WS disconnected driver_id=%s", driver_id)


# ---------------------------------------------------------------------------
# WebSocket — Passengers
# ---------------------------------------------------------------------------

@router.websocket("/ws/passengers")
async def ws_passengers(
    ws: WebSocket,
    user_id: UUID,
    ride_id: UUID | None = None,
    manager: WebSocketManager = Depends(get_ws_manager),
) -> None:
    """
    Passenger real-time channel.
    Query params:
        user_id  — passenger UUID
        ride_id  — (optional) subscribe to a specific ride channel
    Receives: RIDE_CREATED, DRIVER_MATCHED, DRIVER_ASSIGNED, STOP_UPDATED,
              RIDE_STARTED, RIDE_COMPLETED, RIDE_CANCELLED
    """
    await manager.connect_passenger(user_id, ws)
    if ride_id:
        manager.subscribe_to_ride(ride_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        pass
    finally:
        if ride_id:
            manager.unsubscribe_from_ride(ride_id, ws)
        await manager.disconnect_passenger(user_id, ws)
        logger.info("Passenger WS disconnected user_id=%s", user_id)
