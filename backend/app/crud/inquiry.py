"""inquiries 테이블 조회."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Inquiry, InquiryStatus


async def count_by_status(session: AsyncSession, status: InquiryStatus) -> int:
    count = await session.scalar(
        select(func.count()).select_from(Inquiry).where(Inquiry.status == status)
    )
    return count or 0
