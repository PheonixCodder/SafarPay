class PaymentDomainError(Exception):
    """Base payment domain error."""


class WalletFrozenError(PaymentDomainError):
    """Wallet is frozen."""


class InsufficientWalletBalanceError(PaymentDomainError):
    """Wallet cannot cover the requested reserve/debit."""


class ReservationNotFoundError(PaymentDomainError):
    """Commission reservation was not found."""


class PaymentIntentNotFoundError(PaymentDomainError):
    """Payment intent was not found."""


class DuplicateFinancialOperationError(PaymentDomainError):
    """Idempotency key was already processed with incompatible data."""
