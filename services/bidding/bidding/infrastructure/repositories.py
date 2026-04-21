"""Bidding concrete repository."""
from __future__ import annotations

from uuid import UUID

from sp.infrastructure.db.repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import Bid, BidStatus
from .orm_models import BidORM


class BidRepository(BaseRepository[BidORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BidORM)

    async def find_by_item(self, item_id: str) -> list[Bid]:
        result = await self._session.execute(
            select(BidORM).where(BidORM.item_id == item_id).order_by(BidORM.amount.desc())
        )
        return [self._to_domain(o) for o in result.scalars().all()]

    async def find_by_id(self, bid_id: UUID) -> Bid | None:  # type: ignore[override]
        orm = await super().find_by_id(bid_id)
        return self._to_domain(orm) if orm else None

    async def get_highest_bid(self, item_id: str) -> float | None:
        result = await self._session.execute(
            select(BidORM.amount)
            .where(BidORM.item_id == item_id)
            .order_by(BidORM.amount.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save(self, bid: Bid) -> Bid:  # type: ignore[override]
        orm = BidORM(
            id=bid.id,
            item_id=bid.item_id,
            bidder_id=bid.bidder_id,
            amount=bid.amount,
            status=bid.status.value,
            placed_at=bid.placed_at,
        )
        saved = await super().save(orm)
        return self._to_domain(saved)

    @staticmethod
    def _to_domain(orm: BidORM) -> Bid:
        return Bid(
            id=orm.id,
            item_id=orm.item_id,
            bidder_id=orm.bidder_id,
            amount=orm.amount,
            status=BidStatus(orm.status),
            placed_at=orm.placed_at,
        )
