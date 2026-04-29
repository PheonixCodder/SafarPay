"""Ride service domain exceptions.

All exceptions are pure Python — no FastAPI, SQLAlchemy, or any
framework dependency. The API layer is responsible for translating
these into appropriate HTTP responses.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class RideDomainError(Exception):
    """Base exception for all ride domain errors."""


# ---------------------------------------------------------------------------
# Ride aggregate
# ---------------------------------------------------------------------------

class RideNotFoundError(RideDomainError):
    """Raised when a service request cannot be found."""


class InvalidStateTransitionError(RideDomainError):
    """Raised on an illegal ride lifecycle state change.

    Example: trying to start a ride before it has been accepted.
    """


class RideAlreadyCancelledError(RideDomainError):
    """Raised when attempting an action on a cancelled ride."""


class RideAlreadyCompletedError(RideDomainError):
    """Raised when attempting an action on a completed ride."""


class RideNotAssignedError(RideDomainError):
    """Raised when a driver action requires an assigned driver but none is set."""


class ServiceTypeDetailMismatchError(RideDomainError):
    """Raised when the provided detail payload does not match service_type.

    Example: sending CityRideDetail for a FREIGHT service type.
    """


class InsufficientStopsError(RideDomainError):
    """Raised when a ride does not have the required minimum stops.

    Every ride requires at least one PICKUP and one DROPOFF.
    """


class DuplicateStopSequenceError(RideDomainError):
    """Raised when two stops share the same sequence_order on the same ride."""


class UnauthorisedRideAccessError(RideDomainError):
    """Raised when the requester does not own or is not assigned to the ride."""


# ---------------------------------------------------------------------------
# Stop entity
# ---------------------------------------------------------------------------

class StopNotFoundError(RideDomainError):
    """Raised when a stop cannot be found."""


class StopSequenceError(RideDomainError):
    """Raised on invalid stop ordering or sequence conflicts."""


class StopNotArrivedError(RideDomainError):
    """Raised when completing a stop before the driver has arrived."""


class StopAlreadyArrivedError(RideDomainError):
    """Raised when marking arrival on a stop that is already arrived."""


class StopAlreadyCompletedError(RideDomainError):
    """Raised when re-completing an already-completed stop."""


# ---------------------------------------------------------------------------
# Verification code entity
# ---------------------------------------------------------------------------

class VerificationCodeNotFoundError(RideDomainError):
    """Raised when no active verification code exists for a ride/stop."""


class VerificationCodeExpiredError(RideDomainError):
    """Raised when a verification code has passed its expiry time."""


class VerificationCodeExhaustedError(RideDomainError):
    """Raised when max verification attempts have been reached."""


class VerificationCodeAlreadyVerifiedError(RideDomainError):
    """Raised when attempting to verify an already-verified code."""


class VerificationCodeInvalidError(RideDomainError):
    """Raised when the submitted code does not match the stored code."""


# ---------------------------------------------------------------------------
# Proof image
# ---------------------------------------------------------------------------

class ProofUploadError(RideDomainError):
    """Raised when proof image metadata is invalid or upload context is wrong."""


class InvalidMimeTypeError(ProofUploadError):
    """Raised when the uploaded file has a disallowed MIME type."""
