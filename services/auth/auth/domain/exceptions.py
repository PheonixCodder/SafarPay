"""Auth domain exceptions — typed errors that map to HTTP responses in api/router.py."""


class AuthDomainError(Exception):
    """Base for all auth domain exceptions."""


class InvalidCredentialsError(AuthDomainError):
    """Raised when login credentials are wrong."""


class UserNotFoundError(AuthDomainError):
    """Raised when a user cannot be located by id or email."""


class UserAlreadyExistsError(AuthDomainError):
    """Raised when attempting to register a duplicate email or phone."""


class InactiveUserError(AuthDomainError):
    """Raised when a deactivated account attempts to authenticate."""


class TokenExpiredError(AuthDomainError):
    """Raised when a JWT token has passed its expiry."""


class InvalidSessionError(AuthDomainError):
    """Raised when a refresh token maps to no active session."""


class OTPExpiredError(AuthDomainError):
    """Raised when the OTP has expired or was already used."""


class OTPInvalidError(AuthDomainError):
    """Raised when the OTP code does not match."""


class OTPMaxAttemptsError(AuthDomainError):
    """Raised when too many OTP verification attempts have been made."""


class OTPRateLimitError(AuthDomainError):
    """Raised when OTP send/verify rate limit is exceeded."""


class GoogleTokenError(AuthDomainError):
    """Raised when Google id_token verification fails."""


class InvalidVerificationTokenError(AuthDomainError):
    """Raised when the phone verification_token is invalid or expired."""


class PhoneAlreadyLinkedError(AuthDomainError):
    """Raised when trying to link a phone that belongs to another account (pre-merge info)."""
