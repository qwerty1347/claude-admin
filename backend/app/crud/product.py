"""products 테이블 조회."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product


async def count_low_stock(session: AsyncSession, threshold: int) -> int:
    """재고가 threshold 보다 적은 상품 수"""
    count = await session.scalar(
        select(func.count()).select_from(Product).where(Product.stock < threshold)
    )
    return count or 0
