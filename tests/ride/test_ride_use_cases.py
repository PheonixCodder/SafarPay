from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

import pytest
from ride.application.schemas import (
    AcceptRideRequest,
    AddStopRequest,
    CancelRideRequest,
    CreateRideRequest,
    GenerateVerificationCodeRequest,
    ProofUploadUrlRequest,
    UploadProofRequest,
    VerifyAndCompleteRequest,
    VerifyAndStartRequest,
    VerifyCodeRequest,
)
from ride.application.use_cases import (
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
    InternalAssignDriverUseCase,
    MarkStopArrivedUseCase,
    MarkStopCompletedUseCase,
    StartRideUseCase,
    UploadProofUseCase,
    VerifyVerificationCodeUseCase,
)
from ride.domain.exceptions import (
    InvalidStateTransitionError,
    StopNotArrivedError,
    UnauthorisedRideAccessError,
    VerificationCodeInvalidError,
    VerificationCodeNotFoundError,
)
from ride.domain.models import PricingMode, ProofType, RideStatus, StopType

from tests.ride.conftest import (
    DRIVER_ID,
    OTHER_DRIVER_ID,
    OTHER_USER_ID,
    PASSENGER_ID,
    FakeCache,
    FakeCodeRepo,
    FakeGeo,
    FakeProofRepo,
    FakePublisher,
    FakeRideRepo,
    FakeRideWebSockets,
    FakeStopRepo,
    FakeStorage,
    FakeWebhook,
    make_code,
    make_proof,
    make_ride,
    ride_payload,
)


def create_request(pricing_mode: str = "FIXED") -> CreateRideRequest:
    return CreateRideRequest.model_validate(ride_payload(pricing_mode))


@pytest.mark.asyncio
@pytest.mark.parametrize("pricing_mode", ["FIXED", "BID_BASED", "HYBRID"])
async def test_create_ride_enters_matching_and_publishes_pricing_contract(pricing_mode: str) -> None:
    repo = FakeRideRepo()
    cache = FakeCache()
    ws = FakeRideWebSockets()
    publisher = FakePublisher()
    uc = CreateRideUseCase(cast(Any, repo), cast(Any, cache), cast(Any, ws), cast(Any, publisher))

    response = await uc.execute(create_request(pricing_mode), PASSENGER_ID)

    assert response.status == RideStatus.MATCHING
    assert response.pricing_mode.value == pricing_mode
    assert repo.created_detail is not None
    assert repo.created_detail["service_type"] == "CITY_RIDE"
    assert cache.sets[0][0] == "ride"
    assert ws.passenger_events[0][0] == PASSENGER_ID
    payload = publisher.events[0].payload
    assert payload["passenger_user_id"] == str(PASSENGER_ID)
    assert payload["pricing_mode"] == pricing_mode
    assert payload["baseline_min_price"] == 400.0


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda p: p["stops"][1].update({"stop_type": "PICKUP"}), "At least one DROPOFF"),
        (lambda p: p["stops"].append({**p["stops"][0]}), "sequence_order"),
        (lambda p: p.update({"baseline_min_price": 600}), "baseline_min_price"),
        (lambda p: p.update({"service_type": "FREIGHT"}), "does not match"),
    ],
)
def test_create_ride_schema_rejects_invalid_contracts(mutation: Any, message: str) -> None:
    payload = ride_payload()
    mutation(payload)

    with pytest.raises(ValueError, match=message):
        CreateRideRequest.model_validate(payload)


@pytest.mark.asyncio
async def test_fixed_accept_assigns_driver_but_bidding_modes_reject_direct_accept() -> None:
    fixed_ride = make_ride(pricing_mode=PricingMode.FIXED)
    repo = FakeRideRepo(fixed_ride)
    ws = FakeRideWebSockets()
    uc = AcceptRideUseCase(cast(Any, repo), cast(Any, FakeCache()), cast(Any, ws), cast(Any, FakePublisher()))

    response = await uc.execute(fixed_ride.id, AcceptRideRequest(), DRIVER_ID)

    assert response.assigned_driver_id == DRIVER_ID
    assert response.status == RideStatus.ACCEPTED
    assert repo.status_updates[0][2]["assigned_driver_id"] == DRIVER_ID
    assert ws.driver_events[0][0] == DRIVER_ID

    hybrid_ride = make_ride(pricing_mode=PricingMode.HYBRID)
    with pytest.raises(InvalidStateTransitionError, match="Bidding Service"):
        await AcceptRideUseCase(
            cast(Any, FakeRideRepo(hybrid_ride)),
            cast(Any, FakeCache()),
            cast(Any, FakeRideWebSockets()),
        ).execute(hybrid_ride.id, AcceptRideRequest(), DRIVER_ID)


@pytest.mark.asyncio
async def test_internal_assignment_accepts_bidding_ride_with_final_price() -> None:
    ride = make_ride(pricing_mode=PricingMode.BID_BASED)
    repo = FakeRideRepo(ride)

    response = await InternalAssignDriverUseCase(
        cast(Any, repo),
        cast(Any, FakeCache()),
        cast(Any, FakeRideWebSockets()),
        cast(Any, FakePublisher()),
    ).execute(ride.id, DRIVER_ID, final_price=375.0)

    assert response.assigned_driver_id == DRIVER_ID
    assert response.final_price == 375.0
    assert repo.status_updates[0][2]["final_price"] == 375.0


@pytest.mark.asyncio
async def test_cancel_is_passenger_owned_and_notifies_assigned_driver() -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    repo = FakeRideRepo(ride)
    cache = FakeCache()
    ws = FakeRideWebSockets()

    response = await CancelRideUseCase(
        cast(Any, repo),
        cast(Any, cache),
        cast(Any, ws),
        cast(Any, FakePublisher()),
    ).execute(ride.id, CancelRideRequest(reason="changed plans"), PASSENGER_ID)

    assert response.status == RideStatus.CANCELLED
    assert cache.deletes == [("ride", str(ride.id))]
    assert ws.driver_events[0][0] == DRIVER_ID

    with pytest.raises(UnauthorisedRideAccessError):
        other_ride = make_ride()
        await CancelRideUseCase(
            cast(Any, FakeRideRepo(other_ride)),
            cast(Any, FakeCache()),
            cast(Any, FakeRideWebSockets()),
        ).execute(other_ride.id, CancelRideRequest(reason=None), OTHER_USER_ID)


@pytest.mark.asyncio
async def test_start_and_complete_require_assigned_driver_and_otp_when_enabled() -> None:
    ride = make_ride(
        driver_id=DRIVER_ID,
        status=RideStatus.ARRIVING,
        requires_otp_start=True,
        requires_otp_end=True,
    )
    code_repo = FakeCodeRepo(make_code(ride.id))

    with pytest.raises(VerificationCodeNotFoundError):
        await StartRideUseCase(
            cast(Any, FakeRideRepo(ride)),
            cast(Any, code_repo),
            cast(Any, FakeCache()),
            cast(Any, FakeRideWebSockets()),
        ).execute(ride.id, VerifyAndStartRequest(verification_code=None), DRIVER_ID)

    with pytest.raises(UnauthorisedRideAccessError):
        await StartRideUseCase(
            cast(Any, FakeRideRepo(ride)),
            cast(Any, code_repo),
            cast(Any, FakeCache()),
            cast(Any, FakeRideWebSockets()),
        ).execute(ride.id, VerifyAndStartRequest(verification_code="123456"), OTHER_DRIVER_ID)

    started = await StartRideUseCase(
        cast(Any, FakeRideRepo(ride)),
        cast(Any, code_repo),
        cast(Any, FakeCache()),
        cast(Any, FakeRideWebSockets()),
    ).execute(ride.id, VerifyAndStartRequest(verification_code="123456"), DRIVER_ID)

    assert started.status == RideStatus.IN_PROGRESS
    assert code_repo.updated[0].verified_by_driver_id == DRIVER_ID

    end_code_repo = FakeCodeRepo(make_code(ride.id))
    completed = await CompleteRideUseCase(
        cast(Any, FakeRideRepo(ride)),
        cast(Any, end_code_repo),
        cast(Any, FakeCache()),
        cast(Any, FakeRideWebSockets()),
        cast(Any, FakePublisher()),
    ).execute(ride.id, VerifyAndCompleteRequest(verification_code="123456", final_price=410), DRIVER_ID)

    assert completed.status == RideStatus.COMPLETED
    assert end_code_repo.updated[0].verified_by_driver_id == DRIVER_ID


@pytest.mark.asyncio
async def test_invalid_otp_attempt_is_recorded_without_transitioning() -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED, requires_otp_start=True)
    code = make_code(ride.id)
    code_repo = FakeCodeRepo(code)

    with pytest.raises(VerificationCodeInvalidError):
        await StartRideUseCase(
            cast(Any, FakeRideRepo(ride)),
            cast(Any, code_repo),
            cast(Any, FakeCache()),
            cast(Any, FakeRideWebSockets()),
        ).execute(ride.id, VerifyAndStartRequest(verification_code="000000"), DRIVER_ID)

    assert code.attempts == 1
    assert ride.status == RideStatus.ACCEPTED


@pytest.mark.asyncio
async def test_stop_lifecycle_requires_arrival_and_assigned_driver() -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    stop = ride.stops[0]
    stop_repo = FakeStopRepo(stop)
    repo = FakeRideRepo(ride)

    with pytest.raises(UnauthorisedRideAccessError):
        await MarkStopArrivedUseCase(
            cast(Any, repo),
            cast(Any, stop_repo),
            cast(Any, FakeRideWebSockets()),
        ).execute(stop.id, OTHER_DRIVER_ID)

    arrived = await MarkStopArrivedUseCase(
        cast(Any, repo),
        cast(Any, stop_repo),
        cast(Any, FakeRideWebSockets()),
        cast(Any, FakePublisher()),
    ).execute(stop.id, DRIVER_ID)

    assert arrived.arrived_at is not None
    assert ride.status == RideStatus.ARRIVING
    assert stop_repo.arrived[0][0] == stop.id

    completed = await MarkStopCompletedUseCase(
        cast(Any, repo),
        cast(Any, stop_repo),
        cast(Any, FakeRideWebSockets()),
        cast(Any, FakePublisher()),
    ).execute(stop.id, DRIVER_ID)

    assert completed.completed_at is not None

    fresh_ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    fresh_stop = fresh_ride.stops[0]
    with pytest.raises(StopNotArrivedError):
        await MarkStopCompletedUseCase(
            cast(Any, FakeRideRepo(fresh_ride)),
            cast(Any, FakeStopRepo(fresh_stop)),
            cast(Any, FakeRideWebSockets()),
        ).execute(fresh_stop.id, DRIVER_ID)


@pytest.mark.asyncio
async def test_add_stop_rejects_inactive_ride_and_broadcasts_active_ride() -> None:
    ride = make_ride(status=RideStatus.ACCEPTED)
    stop_repo = FakeStopRepo()
    ws = FakeRideWebSockets()
    response = await AddStopUseCase(
        cast(Any, FakeRideRepo(ride)),
        cast(Any, stop_repo),
        cast(Any, ws),
    ).execute(
        ride.id,
        AddStopRequest(
            sequence_order=3,
            stop_type=StopType.WAYPOINT,
            latitude=31.7,
            longitude=74.5,
            place_name=None,
            address_line_1=None,
            city=None,
            country=None,
            contact_name=None,
            contact_phone=None,
        ),
    )

    assert response.sequence_order == 3
    assert ws.passenger_events[0][0] == PASSENGER_ID

    cancelled = make_ride(status=RideStatus.CANCELLED)
    with pytest.raises(Exception, match="inactive"):
        await AddStopUseCase(
            cast(Any, FakeRideRepo(cancelled)),
            cast(Any, FakeStopRepo()),
            cast(Any, FakeRideWebSockets()),
        ).execute(
            cancelled.id,
            AddStopRequest(
                sequence_order=3,
                stop_type=StopType.WAYPOINT,
                latitude=31.7,
                longitude=74.5,
                place_name=None,
                address_line_1=None,
                city=None,
                country=None,
                contact_name=None,
                contact_phone=None,
            ),
        )


@pytest.mark.asyncio
async def test_verification_code_generate_and_verify_tracks_user_or_driver_separately() -> None:
    ride = make_ride()
    code_repo = FakeCodeRepo()
    generated = await GenerateVerificationCodeUseCase(
        cast(Any, FakeRideRepo(ride)),
        cast(Any, code_repo),
        cast(Any, FakePublisher()),
    ).execute(ride.id, GenerateVerificationCodeRequest(length=6, max_attempts=3))

    assert generated.max_attempts == 3
    code = code_repo.created[0]
    verified = await VerifyVerificationCodeUseCase(
        cast(Any, FakeRideRepo(ride)),
        cast(Any, code_repo),
        cast(Any, FakePublisher()),
    ).execute(ride.id, VerifyCodeRequest(code=code.code, user_id=PASSENGER_ID))

    assert verified.is_verified is True
    assert code.verified_by_user_id == PASSENGER_ID
    assert code.verified_by_driver_id is None


@pytest.mark.asyncio
async def test_proof_flow_keeps_passenger_user_id_and_driver_id_separate() -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    proof_repo = FakeProofRepo()
    upload_uc = UploadProofUseCase(cast(Any, FakeRideRepo(ride)), cast(Any, proof_repo), cast(Any, FakePublisher()))

    passenger_proof = await upload_uc.execute(
        ride.id,
        UploadProofRequest(
            proof_type=ProofType.PICKUP,
            file_key="proofs/passenger.jpg",
            file_name=None,
            mime_type=None,
            file_size_bytes=None,
            checksum_sha256=None,
        ),
        uploader_user_id=PASSENGER_ID,
    )
    driver_proof = await upload_uc.execute(
        ride.id,
        UploadProofRequest(
            proof_type=ProofType.DROPOFF,
            file_key="proofs/driver.jpg",
            file_name=None,
            mime_type=None,
            file_size_bytes=None,
            checksum_sha256=None,
        ),
        uploader_driver_id=DRIVER_ID,
    )

    assert passenger_proof.uploaded_by_user_id == PASSENGER_ID
    assert passenger_proof.uploaded_by_driver_id is None
    assert driver_proof.uploaded_by_driver_id == DRIVER_ID
    assert driver_proof.uploaded_by_user_id is None

    with pytest.raises(UnauthorisedRideAccessError):
        await upload_uc.execute(
            ride.id,
            UploadProofRequest(
                proof_type=ProofType.PICKUP,
                file_key="bad.jpg",
                file_name=None,
                mime_type=None,
                file_size_bytes=None,
                checksum_sha256=None,
            ),
            uploader_driver_id=OTHER_DRIVER_ID,
        )


@pytest.mark.asyncio
async def test_presigned_proof_urls_authorize_only_passenger_driver_or_uploader() -> None:
    ride = make_ride(driver_id=DRIVER_ID, status=RideStatus.ACCEPTED)
    storage = FakeStorage()
    put = await GenerateProofUploadUrlUseCase(
        cast(Any, FakeRideRepo(ride)),
        cast(Any, storage),
    ).execute(
        ride.id,
        ProofUploadUrlRequest(proof_type=ProofType.PICKUP, file_name="pickup.jpg", stop_id=None),
        actor_user_id=DRIVER_ID,
    )

    assert put.file_key.endswith(".jpg")
    assert put.presigned_url.startswith("https://s3.test/put/")

    proof = make_proof(ride.id, user_id=None, driver_id=DRIVER_ID)
    got = await GetProofWithUrlUseCase(
        cast(Any, FakeProofRepo([proof])),
        cast(Any, storage),
    ).execute(ride.id, proof.id, actor_user_id=DRIVER_ID)

    assert got.view_url.startswith("https://s3.test/get/")

    with pytest.raises(UnauthorisedRideAccessError):
        await GetProofWithUrlUseCase(
            cast(Any, FakeProofRepo([proof])),
            cast(Any, storage),
        ).execute(ride.id, proof.id, actor_user_id=OTHER_USER_ID)


@pytest.mark.asyncio
async def test_nearby_driver_matching_and_broadcast_records_events() -> None:
    cache = FakeCache()
    publisher = FakePublisher()
    geo = FakeGeo()
    nearby = await FindNearbyDriversUseCase(
        cast(Any, geo),
        cast(Any, cache),
        cast(Any, publisher),
    ).execute(31.5, 74.3, 5, ride_id=uuid4(), category="MINI", vehicle_type="SEDAN")

    assert nearby.count == 1
    assert geo.calls[0]["category"] == "MINI"
    assert cache.sets[0][0] == "ride:candidates"

    ws = FakeRideWebSockets()
    webhook = FakeWebhook()
    await BroadcastRideToDriversUseCase(
        cast(Any, cache),
        cast(Any, ws),
        cast(Any, webhook),
        cast(Any, publisher),
    ).execute(uuid4(), geo.candidates, {"pricing_mode": "FIXED"})

    assert ws.driver_broadcasts[0][0] == [DRIVER_ID]
    assert webhook.jobs[0][0] == DRIVER_ID
