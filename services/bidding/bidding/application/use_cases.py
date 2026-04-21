"""Bidding use cases — business logic for place bid and retrieve bids."""
from __future__ import annotations

import logging

from sp.infrastructure.cache.manager import CacheManager
from sp.infrastructure.messaging.events import BidPlacedEvent
from sp.infrastructure.messaging.publisher import EventPublisher
from sp.infrastructure.security.jwt import TokenPayload

from ..domain.exceptions import BidTooLowError
from ..domain.interfaces import BidRepositoryProtocol
from ..domain.models import Bid
from .schemas import BidResponse, ItemBidsResponse, PlaceBidRequest

logger = logging.getLogger("bidding.use_cases")

MINIMUM_BID_INCREMENT = 0.01


class PlaceBidUseCase:
    def __init__(
        self,
        repo: BidRepositoryProtocol,
        cache: CacheManager,
        publisher: EventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._publisher = publisher

    async def execute(self, req: PlaceBidRequest, bidder: TokenPayload) -> BidResponse:
        # Check current highest bid from cache (fast path)
        current_high: float | None = await self._cache.get(
            "bids", f"highest:{req.item_id}"
        )
        if current_high and req.amount <= float(current_high):
            raise BidTooLowError(
                f"Bid of {req.amount} must exceed current highest: {current_high}"
            )

        bid = Bid.create(
            item_id=req.item_id,
            bidder_id=bidder.user_id,
            amount=req.amount,
        )
        saved = await self._repo.save(bid)

        # Update cache
        await self._cache.set("bids", f"highest:{req.item_id}", req.amount, ttl=3600)

        if self._publisher:
            await self._publisher.publish(
                BidPlacedEvent(
                    payload={
                        "bid_id": str(saved.id),
                        "item_id": saved.item_id,
                        "bidder_id": str(saved.bidder_id),
                        "amount": saved.amount,
                    }
                )
            )

        logger.info("Bid placed item=%s amount=%s", saved.item_id, saved.amount)
        return _to_response(saved)


class GetItemBidsUseCase:
    def __init__(self, repo: BidRepositoryProtocol, cache: CacheManager) -> None:
        self._repo = repo
        self._cache = cache

    async def execute(self, item_id: str) -> ItemBidsResponse:
        bids = await self._repo.find_by_item(item_id)
        highest = await self._cache.get("bids", f"highest:{item_id}")
        return ItemBidsResponse(
            item_id=item_id,
            bids=[_to_response(b) for b in bids],
            highest_bid=float(highest) if highest else None,
        )


def _to_response(bid: Bid) -> BidResponse:
    return BidResponse(
        id=bid.id,
        item_id=bid.item_id,
        bidder_id=bid.bidder_id,
        amount=bid.amount,
        status=bid.status.value,
        placed_at=bid.placed_at,
    )
