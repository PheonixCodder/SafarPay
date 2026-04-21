"""Auth domain exceptions — typed errors that map to HTTP responses in api/router.py."""


class AuthDomainError(Exception):
    """Base for all auth domain exceptions."""


class InvalidCredentialsError(AuthDomainError):
    """Raised when login credentials are wrong."""


class UserNotFoundError(AuthDomainError):
    """Raised when a user cannot be located by id or email."""


class UserAlreadyExistsError(AuthDomainError):
    """Raised when attempting to register a duplicate email."""


class InactiveUserError(AuthDomainError):
    """Raised when a deactivated account attempts to authenticate."""


class TokenExpiredError(AuthDomainError):
    """Raised when a JWT token has passed its expiry."""
