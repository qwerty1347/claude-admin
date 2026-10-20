"""대시보드 응답 스키마. 프론트 src/types/dashboard.ts 와 1:1 로 맞춘다 (둘은 함께 수정한다)."""

from typing import Literal

from pydantic import AwareDatetime

from app.schemas.common import CamelModel

ComparePeriod = Literal["day", "week", "month"]


class KpiComparison(CamelModel):
    """같은 기간끼리 비교한 값. 증감률·차이는 프론트가 계산한다."""

    period: ComparePeriod
    """day: 오늘 vs 어제 같은 시각 / week: 이번 주 vs 지난주 / month: 이번 달 vs 지난달"""
    current: int | float
    previous: int | float


class Kpi(CamelModel):
    key: Literal["revenue", "orders", "signups", "conversion"]
    label: str
    value: int | float  # 이번 달 값. 금액·건수는 정수, 전환율 등은 실수
    unit: Literal["won", "count", "percent"]
    change: float
    """지난달 대비 증감. count·won 은 %, percent 는 %p"""
    comparisons: list[KpiComparison] = []
    """전일·지난주·지난달 비교 (대시보드 하단 KPI 의 굴러가는 띠)"""


class RevenueTrend(CamelModel):
    months: list[str]
    revenue: list[int]
    orders: list[int]
    last_year_same_month_revenue: int
    """작년 같은 달(이번 달의 1년 전) 매출 — 전년 동월 비교용"""


class CategoryShare(CamelModel):
    name: str
    value: int


class TrafficSource(CamelModel):
    channel: str
    visitors: int


class HourlyTraffic(CamelModel):
    days: list[str]
    hours: list[str]
    values: list[tuple[int, int, int]]
    """[hourIndex, dayIndex, value]"""


OrderStatus = Literal["paid", "shipping", "delivered", "cancelled"]


class RecentOrder(CamelModel):
    """TS 의 Order"""

    id: str
    customer: str
    amount: int
    status: OrderStatus
    ordered_at: AwareDatetime
    """타임존 포함 시각. JSON: 2026-09-30T13:42:00+09:00"""


class TodoItem(CamelModel):
    key: str
    label: str
    count: int
    unit: Literal["건", "개"]
    href: str
    urgent: bool = False
    """바로 처리해야 하는 항목은 강조"""


class TodoSummary(CamelModel):
    items: list[TodoItem]
    done_today: int
    """오늘 이미 처리한 건수"""


class TodayRevenue(CamelModel):
    today: int
    """오늘 0시부터 지금까지 매출"""
    yesterday_same_time: int
    """어제 0시부터 같은 시각까지 매출"""
