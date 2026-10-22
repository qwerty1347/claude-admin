from datetime import datetime
from typing import Literal

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, KSTDateTime
from app.models.customer import Customer

# DB 에는 문자열로 저장한다 (ENUM 은 값이 바뀔 때마다 마이그레이션이 필요해서 쓰지 않는다)
# paid: 결제 완료 = 발송 대기
OrderStatus = Literal["paid", "shipping", "delivered", "cancelled", "refund_requested"]


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(30), unique=True)
    """화면에 보이는 주문 번호. 예: ORD-260930-1042"""
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    amount: Mapped[int]
    status: Mapped[str] = mapped_column(String(20), index=True)
    """OrderStatus 값 중 하나"""
    ordered_at: Mapped[datetime] = mapped_column(KSTDateTime, index=True)
    shipped_at: Mapped[datetime | None] = mapped_column(KSTDateTime)

    # 비동기에서는 지연 로딩이 에러가 나므로 막아 두고, 필요하면 selectinload/joinedload 로 불러온다
    customer: Mapped[Customer] = relationship(lazy="raise")
