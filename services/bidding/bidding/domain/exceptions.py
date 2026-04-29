"""Bidding domain exceptions."""


class BiddingDomainError(Exception):
    """Base for all bidding domain exceptions."""


class BidTooLowError(BiddingDomainError):
    """Raised when a bid is below the current minimum."""


class BiddingClosedError(BiddingDomainError):
    """Raised when bidding is no longer open for an item."""


class InvalidBidderError(BiddingDomainError):
    """Raised when the bidder is not eligible to bid."""


class BiddingSessionNotFoundError(BiddingDomainError):
    """Raised when a bidding session cannot be found."""


class BidNotFoundError(BiddingDomainError):
    """Raised when a specific bid cannot be found."""


class LockAcquisitionError(BiddingDomainError):
    """Raised when a Redis lock cannot be acquired."""


class UnauthorisedBiddingAccessError(BiddingDomainError):
    """Raised when a user attempts an unauthorised action on a bidding session."""
