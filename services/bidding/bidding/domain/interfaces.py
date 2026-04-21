"""Bidding repository protocol."""
from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .models import Bid


class BidRepositoryProtocol(Protocol):
    async def find_by_id(self, bid_id: UUID) -> Bid | None: ...
    async def find_by_item(self, item_id: str) -> list[Bid]: ...
    async def save(self, bid: Bid) -> Bid: ...
    async def get_highest_bid(self, item_id: str) -> float | None: ...
