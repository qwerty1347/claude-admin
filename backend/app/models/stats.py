"""대시보드 집계 테이블. 미리 계산해 둔 통계를 화면이 그대로 읽는다.

지금은 시드(app/initial_data.py)가 채우고, 실제 주문이 쌓이면 배치 작업이 orders 등을 집계해서 채운다.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# 비율(%)은 소수 둘째 자리까지 정확히 저장한다 (예: 3.46)
Rate = Numeric(5, 2)


class MonthlyMetric(Base):
    """월별 핵심 지표 (revenue-trend, kpis 의 이번 달·지난달)"""

    __tablename__ = "monthly_metrics"

    year_month: Mapped[str] = mapped_column(String(7), primary_key=True)
    """예: 2026-09"""
    revenue: Mapped[int] = mapped_column(BigInteger)
    orders: Mapped[int]
    signups: Mapped[int]
    conversion_rate: Mapped[Decimal] = mapped_column(Rate)


class MonthlyCategorySale(Base):
    """월별 카테고리 매출 (category-shares)"""

    __tablename__ = "monthly_category_sales"

    year_month: Mapped[str] = mapped_column(String(7), primary_key=True)
    category: Mapped[str] = mapped_column(String(30), primary_key=True)
    revenue: Mapped[int] = mapped_column(BigInteger)


class MonthlyTrafficSource(Base):
    """월별 유입 경로 방문자 (traffic-sources)"""

    __tablename__ = "monthly_traffic_sources"

    year_month: Mapped[str] = mapped_column(String(7), primary_key=True)
    channel: Mapped[str] = mapped_column(String(50), primary_key=True)
    visitors: Mapped[int]
    sort_order: Mapped[int] = mapped_column(SmallInteger)
    """화면 표시 순서"""


class HourlyVisit(Base):
    """요일·시간대별 방문 (hourly-traffic 히트맵 168칸)"""

    __tablename__ = "hourly_visits"

    weekday: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    """0=월 ~ 6=일"""
    hour: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    """0 ~ 23"""
    visits: Mapped[int]


class DailyMetric(Base):
    """일별 지표 (kpis 의 전일·지난주 비교, todos 의 오늘 처리 건수)"""

    __tablename__ = "daily_metrics"

    day: Mapped[date] = mapped_column(primary_key=True)
    orders: Mapped[int]
    signups: Mapped[int]
    conversion_rate: Mapped[Decimal] = mapped_column(Rate)
    todos_done: Mapped[int]
