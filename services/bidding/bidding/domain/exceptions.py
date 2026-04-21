"""Bidding domain exceptions."""


class BiddingDomainError(Exception):
    """Base for all bidding domain exceptions."""


class BidTooLowError(BiddingDomainError):
    """Raised when a bid is below the current minimum."""


class BiddingClosedError(BiddingDomainError):
    """Raised when bidding is no longer open for an item."""


class InvalidBidderError(BiddingDomainError):
    """Raised when the bidder is not eligible to bid."""
