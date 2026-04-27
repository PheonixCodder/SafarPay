"""FastAPI router for the verification service."""
from fastapi import APIRouter, Depends, HTTPException, status

from ..application.schemas import (
    IdentitySubmissionRequest,
    LicenseSubmissionRequest,
    SelfieSubmissionRequest,
    VehicleSubmissionRequest,
    DocumentUploadUrlsResponse,
    VerificationStatusResponse,
    ReviewSubmissionResponse,
)
from ..application.use_cases import VerificationUseCases
from ..infrastructure.dependencies import (
    CurrentUser,
    DriverRepo,
    VehicleRepo,
    DocumentRepo,
    DriverVehicleRepo,
    StorageProvider,
    Resolver,
    IdentityEngine,
    EventPub,
    VerificationRejectionRepo,
    Cache,
)
from ..domain.exceptions import VerificationDomainError, DriverNotFoundError, InvalidDocumentStateError

router = APIRouter(prefix="/v1/verification", tags=["Driver Verification"])


def get_use_cases(
    driver_repo: DriverRepo,
    vehicle_repo: VehicleRepo,
    document_repo: DocumentRepo,
    driver_vehicle_repo: DriverVehicleRepo,
    storage_provider: StorageProvider,
    resolver: Resolver,
    identity_engine: IdentityEngine,
    event_publisher: EventPub,
    rejection_repo: VerificationRejectionRepo,
    cache: Cache,
) -> VerificationUseCases:
    return VerificationUseCases(
        driver_repo=driver_repo,
        vehicle_repo=vehicle_repo,
        document_repo=document_repo,
        driver_vehicle_repo=driver_vehicle_repo,
        storage_provider=storage_provider,
        rejection_resolver=resolver,
        identity_engine=identity_engine,
        event_publisher=event_publisher,
        rejection_repo=rejection_repo,
        cache_manager=cache,
    )


UseCases = Depends(get_use_cases)


@router.get(
    "/me",
    response_model=VerificationStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_verification_status(
    current_user: CurrentUser,
    use_cases: VerificationUseCases = UseCases,
) -> VerificationStatusResponse:
    """Get the full verification state (aggregated response) for the current user."""
    try:
        return await use_cases.get_verification_status(user_id=current_user.user_id)
    except (VerificationDomainError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.") from e


@router.post(
    "/driver/cnic",
    response_model=DocumentUploadUrlsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_identity(
    request: IdentitySubmissionRequest,
    current_user: CurrentUser,
    use_cases: VerificationUseCases = UseCases,
) -> DocumentUploadUrlsResponse:
    """Submit identity documents and request upload URLs for Front & Back images."""
    try:
        return await use_cases.submit_identity_documents(
            user_id=current_user.user_id, request=request
        )
    except (VerificationDomainError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.") from e


@router.post(
    "/driver/license",
    response_model=DocumentUploadUrlsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_license(
    request: LicenseSubmissionRequest,
    current_user: CurrentUser,
    use_cases: VerificationUseCases = UseCases,
) -> DocumentUploadUrlsResponse:
    """Submit Driving License details and request upload URLs for Front & Back images."""
    try:
        return await use_cases.submit_license_documents(
            user_id=current_user.user_id, request=request
        )
    except (VerificationDomainError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.") from e


@router.post(
    "/driver/selfie",
    response_model=DocumentUploadUrlsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_selfie(
    request: SelfieSubmissionRequest,
    current_user: CurrentUser,
    use_cases: VerificationUseCases = UseCases,
) -> DocumentUploadUrlsResponse:
    """Request upload URL for selfie with driving license."""
    try:
        return await use_cases.submit_selfie(
            user_id=current_user.user_id, request=request
        )
    except (VerificationDomainError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.") from e


@router.post(
    "/driver/vehicle",
    response_model=DocumentUploadUrlsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_vehicle(
    request: VehicleSubmissionRequest,
    current_user: CurrentUser,
    use_cases: VerificationUseCases = UseCases,
) -> DocumentUploadUrlsResponse:
    """Submit Vehicle details and request upload URLs for registration docs and photos."""
    try:
        return await use_cases.submit_vehicle_info_and_documents(
            user_id=current_user.user_id, request=request
        )
    except (VerificationDomainError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.") from e

@router.post("/submit-review", response_model=ReviewSubmissionResponse, status_code=200)
async def submit_for_review(
    current_user: CurrentUser,
    use_cases: VerificationUseCases = UseCases,
) -> ReviewSubmissionResponse:
    try:
        return await use_cases.request_verification_review(user_id=current_user.user_id)
    except (VerificationDomainError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.") from e