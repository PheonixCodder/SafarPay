"""Bidding concrete repository."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING
from uuid import UUID

from sp.infrastructure.db.repository import BaseRepository
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import Bid, BiddingSession, BiddingSessionStatus, BidStatus, CounterOffer, CounterOfferStatus
from .orm_models import RideBiddingSessionORM, RideBidORM, RideBidCounterOfferORM

if TYPE_CHECKING:
    from ..domain.models import CounterOffer


class BidRepository(BaseRepository[RideBidORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RideBidORM)

    async def find_by_session(self, session_id: UUID) -> list[Bid]:
        result = await self._session.execute(
            select(RideBidORM)
            .where(RideBidORM.bidding_session_id == session_id)
            .order_by(RideBidORM.bid_amount.asc())
        )
        return [self._to_domain(o) for o in result.scalars().all()]

    async def find_by_driver_and_session(self, driver_id: UUID, session_id: UUID) -> Bid | None:
        result = await self._session.execute(
            select(RideBidORM)
            .where(
                RideBidORM.bidding_session_id == session_id,
                RideBidORM.driver_id == driver_id
            )
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_id(self, bid_id: UUID) -> Bid | None:  # type: ignore[override]
        orm = await super().find_by_id(bid_id)
        return self._to_domain(orm) if orm else None

    async def save(self, bid: Bid) -> Bid:  # type: ignore[override]
        orm = RideBidORM(
            id=bid.id,
            service_request_id=bid.service_request_id,
            bidding_session_id=bid.bidding_session_id,
            driver_id=bid.driver_id,
            driver_vehicle_id=bid.driver_vehicle_id,
            bid_amount=bid.bid_amount,
            currency=bid.currency,
            eta_minutes=bid.eta_minutes,
            message=bid.message,
            status=bid.status.value,
            expires_at=bid.expires_at,
        )
        saved = await super().save(orm)
        return self._to_domain(saved)

    async def update_status(self, bid_id: UUID, status: str) -> None:
        orm = await super().find_by_id(bid_id)
        if orm:
            orm.status = status # type: ignore[assignment]
            await self._session.flush()

    async def find_lowest_by_session(self, session_id: UUID) -> Bid | None:
        result = await self._session.execute(
            select(RideBidORM)
            .where(RideBidORM.bidding_session_id == session_id, RideBidORM.status == BidStatus.ACTIVE.value)
            .order_by(RideBidORM.bid_amount.asc(), RideBidORM.created_at.asc())
            .limit(1)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def mark_outbid_transactional(self, session_id: UUID, new_lowest_amount: float, placed_at_threshold: Any) -> int:
        from sqlalchemy import update
        result = await self._session.execute(
            update(RideBidORM)
            .where(
                RideBidORM.bidding_session_id == session_id,
                RideBidORM.status == BidStatus.ACTIVE.value,
                (RideBidORM.bid_amount > new_lowest_amount) |
                ((RideBidORM.bid_amount == new_lowest_amount) & (RideBidORM.created_at < placed_at_threshold))
            )
            .values(status=BidStatus.OUTBID.value)
        )
        await self._session.flush()
        return result.rowcount

    async def save_outbox_event(self, bid_id: UUID, event_type: str, payload: dict[str, Any]) -> None:
        import json

        from .orm_models import BidEventType, RideBidEventORM
        event = RideBidEventORM(
            bid_id=bid_id,
            event_type=BidEventType(event_type),
            payload=json.dumps(payload),
        )
        self._session.add(event)
        await self._session.flush()


    @staticmethod
    def _to_domain(orm: RideBidORM) -> Bid:
        return Bid(
            id=orm.id,
            service_request_id=orm.service_request_id,
            bidding_session_id=orm.bidding_session_id,
            driver_id=orm.driver_id,
            bid_amount=float(orm.bid_amount),
            currency=orm.currency,
            status=BidStatus(orm.status),
            driver_vehicle_id=orm.driver_vehicle_id,
            eta_minutes=orm.eta_minutes,
            message=orm.message,
            expires_at=orm.expires_at,
            placed_at=orm.created_at,
        )


class BiddingSessionRepository(BaseRepository[RideBiddingSessionORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RideBiddingSessionORM)

    async def find_by_id(self, session_id: UUID) -> BiddingSession | None: # type: ignore[override]
        orm = await super().find_by_id(session_id)
        return self._to_domain(orm) if orm else None

    async def find_by_ride(self, ride_id: UUID) -> BiddingSession | None:
        result = await self._session.execute(
            select(RideBiddingSessionORM).where(RideBiddingSessionORM.service_request_id == ride_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_active_sessions(self) -> list[BiddingSession]:
        result = await self._session.execute(
            select(RideBiddingSessionORM)
            .where(RideBiddingSessionORM.status == BiddingSessionStatus.OPEN.value)
        )
        return [self._to_domain(o) for o in result.scalars().all()]

    async def save(self, session: BiddingSession) -> BiddingSession:  # type: ignore[override]
        orm = RideBiddingSessionORM(
            id=session.id,
            service_request_id=session.service_request_id,
            status=session.status.value,
            opened_at=session.opened_at,
            expires_at=session.expires_at,
            closed_at=session.closed_at,
            max_bids_allowed=session.max_bids_allowed,
            min_driver_rating=session.min_driver_rating,
            baseline_price=session.baseline_price,
        )
        saved = await super().save(orm)
        return self._to_domain(saved)

    async def update_status(self, session_id: UUID, status: str) -> None:
        orm = await super().find_by_id(session_id)
        if orm:
            orm.status = status # type: ignore[assignment]
            await self._session.flush()

    @staticmethod
    def _to_domain(orm: RideBiddingSessionORM) -> BiddingSession:
        return BiddingSession(
            id=orm.id,
            service_request_id=orm.service_request_id,
            status=BiddingSessionStatus(orm.status),
            opened_at=orm.opened_at,
            expires_at=orm.expires_at,
            closed_at=orm.closed_at,
            max_bids_allowed=orm.max_bids_allowed,
            min_driver_rating=float(orm.min_driver_rating) if orm.min_driver_rating else None,
            baseline_price=float(orm.baseline_price) if orm.baseline_price else None,
        )


class CounterOfferRepository(BaseRepository[RideBidCounterOfferORM]):
    """Repository for bid counter-offers (passenger ↔ driver negotiation)."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RideBidCounterOfferORM)

    async def find_by_id(self, counter_offer_id: UUID) -> RideBidCounterOfferORM | None:
        result = await self._session.execute(
            select(RideBidCounterOfferORM).where(RideBidCounterOfferORM.id == counter_offer_id)
        )
        return result.scalar_one_or_none()

    async def find_active_by_session(self, session_id: UUID) -> list[RideBidCounterOfferORM]:
        """Find all pending counter-offers for a session."""
        result = await self._session.execute(
            select(RideBidCounterOfferORM)
            .where(
                RideBidCounterOfferORM.session_id == session_id,
                RideBidCounterOfferORM.status == CounterOfferStatus.PENDING,
            )
            .order_by(RideBidCounterOfferORM.created_at.desc())
        )
        return result.scalars().all()

    def _to_domain(self, orm: RideBidCounterOfferORM) -> CounterOffer:
        return CounterOffer(
            id=orm.id,
            session_id=orm.session_id,
            price=float(orm.counter_price),
            eta_minutes=orm.counter_eta_minutes,
            user_id=orm.counter_by_user_id,
            driver_id=orm.counter_by_driver_id,
            bid_id=orm.bid_id,  # Map bid_id from ORM to domain
            status=orm.status,
            responded_at=orm.responded_at,
        )

    async def save(self, counter_offer: CounterOffer) -> CounterOffer:
        """Save a domain CounterOffer and return domain object."""
        orm = RideBidCounterOfferORM(
            id=counter_offer.id,
            session_id=counter_offer.session_id,
            counter_price=counter_offer.price,
            counter_eta_minutes=counter_offer.eta_minutes,
            counter_by_user_id=counter_offer.user_id,
            counter_by_driver_id=counter_offer.driver_id,
            bid_id=counter_offer.bid_id,
            status=counter_offer.status,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_domain(orm)

    async def update(self, counter_offer: CounterOffer) -> None:
        """Update a domain CounterOffer in the database."""
        result = await self._session.execute(
            select(RideBidCounterOfferORM).where(RideBidCounterOfferORM.id == counter_offer.id)
        )
        orm = result.scalar_one_or_none()
        if orm:
            orm.status = counter_offer.status
            orm.responded_at = counter_offer.responded_at
        await self._session.flush()
