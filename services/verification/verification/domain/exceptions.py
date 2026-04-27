"""Verification domain exceptions."""


class VerificationDomainError(Exception):
    """Base for all verification domain exceptions."""


class DocumentNotFoundError(VerificationDomainError):
    """Raised when a document cannot be found."""


class UnauthorizedDocumentAccessError(VerificationDomainError):
    """Raised when a user attempts to access another user's document."""


class DocumentAlreadyVerifiedError(VerificationDomainError):
    """Raised when trying to re-submit an already verified document."""

class MLProcessingError(VerificationDomainError):
    """Raised when ML engine fails due to data/model issues, not infrastructure."""
    pass


class DriverNotFoundError(VerificationDomainError):
    """Raised when driver profile does not exist."""
    pass


class InvalidDocumentStateError(VerificationDomainError):
    """Raised when a document is in an invalid state for an operation."""
    pass
