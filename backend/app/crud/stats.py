"""집계 테이블(app/models/stats.py) 조회."""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DailyMetric,
    HourlyVisit,
    MonthlyCategorySale,
    MonthlyMetric,
    MonthlyTrafficSource,
)


async def get_monthly_metrics(
    session: AsyncSession, year_months: Sequence[str]
) -> dict[str, MonthlyMetric]:
    """year_month 별 행. 없는 달은 결과에 없다"""
    rows = await session.scalars(
        select(MonthlyMetric).where(MonthlyMetric.year_month.in_(year_months))
    )
    return {row.year_month: row for row in rows}


async def get_daily_metrics(
    session: AsyncSession, start: date, end: date
) -> dict[date, DailyMetric]:
    """[start, end] (양 끝 포함) 날짜별 행. 없는 날은 결과에 없다"""
    rows = await session.scalars(
        select(DailyMetric).where(DailyMetric.day >= start, DailyMetric.day <= end)
    )
    return {row.day: row for row in rows}


async def get_todos_done(session: AsyncSession, day: date) -> int:
    done = await session.scalar(
        select(DailyMetric.todos_done).where(DailyMetric.day == day)
    )
    return done or 0


async def list_category_sales(
    session: AsyncSession, year_month: str
) -> Sequence[MonthlyCategorySale]:
    """매출 큰 순"""
    rows = await session.scalars(
        select(MonthlyCategorySale)
        .where(MonthlyCategorySale.year_month == year_month)
        .order_by(MonthlyCategorySale.revenue.desc())
    )
    return rows.all()


async def list_traffic_sources(
    session: AsyncSession, year_month: str
) -> Sequence[MonthlyTrafficSource]:
    """화면 표시 순서(sort_order)대로"""
    rows = await session.scalars(
        select(MonthlyTrafficSource)
        .where(MonthlyTrafficSource.year_month == year_month)
        .order_by(MonthlyTrafficSource.sort_order)
    )
    return rows.all()


async def list_hourly_visits(session: AsyncSession) -> Sequence[HourlyVisit]:
    """요일 바깥, 시간 안쪽 순서"""
    rows = await session.scalars(
        select(HourlyVisit).order_by(HourlyVisit.weekday, HourlyVisit.hour)
    )
    return rows.all()
