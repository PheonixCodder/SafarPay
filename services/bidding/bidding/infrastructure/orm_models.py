"""Bidding ORM models — bidding.bids schema."""
from __future__ import annotations

import uuid
from datetime import datetime

from sp.infrastructure.db.base import Base, TimestampMixin
from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class BidORM(Base, TimestampMixin):
    __tablename__ = "bids"
    __table_args__ = {"schema": "bidding"}

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    item_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    bidder_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    placed_at: Mapped[datetime] = mapped_column(nullable=False)
