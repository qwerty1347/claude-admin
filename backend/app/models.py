"""응답 모델. 프론트 src/types/dashboard.ts 와 1:1 로 맞춘다 (둘은 함께 수정한다)."""

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """파이썬에서는 snake_case, JSON 에서는 camelCase (FastAPI 는 응답을 by_alias 로 직렬화한다)."""

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)


class Kpi(CamelModel):
    key: Literal["revenue", "orders", "signups", "conversion"]
    label: str
    value: int | float  # 금액·건수는 정수, 전환율 등은 실수
    unit: Literal["won", "count", "percent"]
    change: float
    """전기 대비 증감률 (%)"""


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
