from datetime import datetime
from typing import Literal

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import clock
from app.core.db import Base, KSTDateTime
from app.models.customer import Customer

InquiryStatus = Literal["pending", "answered"]


class Inquiry(Base):
    """1:1 회원 문의"""

    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str] = mapped_column(String(20), index=True)
    """InquiryStatus 값 중 하나"""
    created_at: Mapped[datetime] = mapped_column(KSTDateTime, default=clock.now)

    customer: Mapped[Customer] = relationship(lazy="raise")
