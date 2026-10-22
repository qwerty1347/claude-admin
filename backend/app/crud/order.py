"""orders 테이블 조회."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Order, OrderStatus


async def sum_amount(session: AsyncSession, start: datetime, end: datetime) -> int:
    """[start, end) 에 들어온 주문 금액 합계"""
    total = await session.scalar(
        select(func.coalesce(func.sum(Order.amount), 0)).where(
            Order.ordered_at >= start, Order.ordered_at < end
        )
    )
    return int(total or 0)


async def count_by_status(
    session: AsyncSession, statuses: Sequence[OrderStatus]
) -> dict[str, int]:
    """상태별 주문 수. 주문이 없는 상태는 결과에 없다"""
    result = await session.execute(
        select(Order.status, func.count())
        .where(Order.status.in_(statuses))
        .group_by(Order.status)
    )
    # Result 는 .keys() 가 있어 dict(result) 로 쓰면 매핑으로 오인된다. 행 목록으로 바꿔 넣는다
    return dict(result.all())


async def list_recent(session: AsyncSession, limit: int) -> Sequence[Order]:
    """최근 주문 (최신순). 고객을 같이 불러온다"""
    rows = await session.scalars(
        select(Order)
        .options(joinedload(Order.customer))
        .order_by(Order.ordered_at.desc())
        .limit(limit)
    )
    return rows.all()
