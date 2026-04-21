"""Bidding domain models — pure Python."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class BidStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class Bid:
    id: UUID
    item_id: str
    bidder_id: UUID
    amount: float
    status: BidStatus
    placed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, item_id: str, bidder_id: UUID, amount: float) -> Bid:
        return cls(
            id=uuid4(),
            item_id=item_id,
            bidder_id=bidder_id,
            amount=amount,
            status=BidStatus.PENDING,
        )
