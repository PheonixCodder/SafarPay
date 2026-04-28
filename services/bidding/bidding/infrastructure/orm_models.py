"""Bidding ORM models — bidding.bids schema."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# =========================================================
# ENUMS
# =========================================================


class BiddingSessionStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    PAUSED = "PAUSED"


class BidStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    OUTBID = "OUTBID"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class CounterOfferStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class BidEventType(enum.Enum):
    BID_PLACED = "BID_PLACED"
    AUTO_ACCEPT_REQUESTED = "AUTO_ACCEPT_REQUESTED"
    BID_UPDATED = "BID_UPDATED"
    BID_WITHDRAWN = "BID_WITHDRAWN"
    BID_ACCEPTED = "BID_ACCEPTED"
    BID_REJECTED = "BID_REJECTED"
    COUNTER_OFFER_CREATED = "COUNTER_OFFER_CREATED"
    COUNTER_OFFER_RESPONDED = "COUNTER_OFFER_RESPONDED"


# =========================================================
# BIDDING SESSION
# =========================================================


class RideBiddingSessionORM(Base, TimestampMixin):
    __tablename__ = "bidding_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one session per ride
        index=True,
    )

    status: Mapped[BiddingSessionStatus] = mapped_column(
        SQLEnum(BiddingSessionStatus, name="bidding_session_status_enum", schema="bidding"),
        default=BiddingSessionStatus.OPEN,
        nullable=False,
        index=True,
    )

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    max_bids_allowed: Mapped[int | None] = mapped_column(Integer)
    min_driver_rating: Mapped[float | None] = mapped_column(Numeric(3, 2))

    # Relationships
    bids: Mapped[list[RideBidORM]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "max_bids_allowed IS NULL OR max_bids_allowed > 0",
            name="ck_bidding_sessions_max_bids_positive",
        ),
        {"schema": "bidding"},
    )


# =========================================================
# BIDS
# =========================================================


class RideBidORM(Base, TimestampMixin):
    __tablename__ = "bids"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    bidding_session_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("bidding.bidding_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    driver_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    driver_vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.driver_vehicles.id", ondelete="SET NULL"),
        nullable=True,
    )

    bid_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    eta_minutes: Mapped[int | None] = mapped_column(Integer)

    message: Mapped[str | None] = mapped_column(Text)

    status: Mapped[BidStatus] = mapped_column(
        SQLEnum(BidStatus, name="bid_status_enum", schema="bidding"),
        default=BidStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    session: Mapped[RideBiddingSessionORM] = relationship(back_populates="bids")

    status_history: Mapped[list[RideBidStatusHistoryORM]] = relationship(
        back_populates="bid", cascade="all, delete-orphan"
    )

    counter_offers: Mapped[list[RideBidCounterOfferORM]] = relationship(
        back_populates="bid", cascade="all, delete-orphan"
    )

    events: Mapped[list[RideBidEventORM]] = relationship(
        back_populates="bid", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "service_request_id",
            "driver_id",
            name="uq_bid_per_driver_per_request",
        ),
        CheckConstraint("bid_amount > 0", name="ck_bid_amount_positive"),
        Index("ix_bids_request_status", "service_request_id", "status"),
        Index("ix_bids_driver_status", "driver_id", "status"),
        {"schema": "bidding"},
    )


# =========================================================
# BID STATUS HISTORY (AUDIT)
# =========================================================


class RideBidStatusHistoryORM(Base):
    __tablename__ = "bid_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    bid_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("bidding.bids.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[BidStatus | None] = mapped_column(
        SQLEnum(BidStatus, name="bid_status_enum", schema="bidding")
    )
    new_status: Mapped[BidStatus] = mapped_column(
        SQLEnum(BidStatus, name="bid_status_enum", schema="bidding"),
        nullable=False,
    )

    changed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True,
    )

    changed_by_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
        nullable=True,
    )

    reason_code: Mapped[str | None] = mapped_column(String(50))
    reason_text: Mapped[str | None] = mapped_column(Text)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    bid: Mapped[RideBidORM] = relationship(back_populates="status_history")

    __table_args__ = (
        Index("ix_bid_status_history_bid_time", "bid_id", "changed_at"),
        {"schema": "bidding"},
    )


# =========================================================
# COUNTER OFFERS (NEGOTIATION)
# =========================================================


class RideBidCounterOfferORM(Base, TimestampMixin):
    __tablename__ = "bid_counter_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    bid_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("bidding.bids.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    counter_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    counter_eta_minutes: Mapped[int | None] = mapped_column(Integer)

    counter_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
    )

    counter_by_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("verification.drivers.id", ondelete="SET NULL"),
    )

    status: Mapped[CounterOfferStatus] = mapped_column(
        SQLEnum(CounterOfferStatus, name="counter_offer_status_enum", schema="bidding"),
        default=CounterOfferStatus.PENDING,
        nullable=False,
    )

    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    bid: Mapped[RideBidORM] = relationship(back_populates="counter_offers")

    __table_args__ = (
        CheckConstraint("counter_price > 0", name="ck_counter_price_positive"),
        {"schema": "bidding"},
    )


# =========================================================
# FINAL ACCEPTANCE (AUDIT SAFE)
# =========================================================


class RideBidAcceptanceORM(Base, TimestampMixin):
    __tablename__ = "bid_acceptances"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    service_request_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("service_request.service_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    bid_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("bidding.bids.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    accepted_by_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True,
    )

    final_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    final_eta_minutes: Mapped[int | None] = mapped_column(Integer)

    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_bid_acceptances_request", "service_request_id"),
        {"schema": "bidding"},
    )


# =========================================================
# EVENT OUTBOX (FOR REAL-TIME / MICROSERVICES)
# =========================================================


class RideBidEventORM(Base):
    __tablename__ = "bid_events"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    bid_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("bidding.bids.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[BidEventType] = mapped_column(
        SQLEnum(BidEventType, name="bid_event_type_enum", schema="bidding"),
        nullable=False,
        index=True,
    )

    payload: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    bid: Mapped[RideBidORM] = relationship(back_populates="events")

    __table_args__ = (
        Index("ix_bid_events_type_time", "event_type", "created_at"),
        Index("ix_bid_events_unprocessed", "processed_at", "error_count"),
        {"schema": "bidding"},
    )
