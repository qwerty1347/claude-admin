"""대시보드 화면 데이터 조립. crud 로 테이블을 읽고, 계산해서 응답 스키마로 만든다.

- 날짜 경계("오늘", "이번 달")는 clock 기준(KST)으로 잡는다.
- 라벨·단위·href 같은 화면 표시 정보는 데이터가 아니므로 여기 상수로 둔다.
- AsyncSession 은 한 번에 쿼리 하나만 실행할 수 있으므로 쿼리는 차례로 await 한다.
"""

from collections.abc import Callable
from datetime import timedelta
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import clock
from app.crud import inquiry as inquiry_crud
from app.crud import order as order_crud
from app.crud import product as product_crud
from app.crud import stats as stats_crud
from app.models import DailyMetric, MonthlyMetric
from app.schemas import (
    CategoryShare,
    ComparePeriod,
    HourlyTraffic,
    Kpi,
    KpiComparison,
    RecentOrder,
    RevenueTrend,
    TodayRevenue,
    TodoItem,
    TodoSummary,
    TrafficSource,
)
from app.utils import percent_change, year_month

DAYS = ["월", "화", "수", "목", "금", "토", "일"]
HOURS = [f"{h}시" for h in range(24)]

RECENT_ORDERS_LIMIT = 7
LOW_STOCK_THRESHOLD = 10
"""재고가 이 값보다 적으면 재고 부족"""

type Pair = tuple[int | float, int | float]
"""(current, previous)"""


def _change(current: float, previous: float, unit: str) -> float:
    """지난달 대비 증감. 비율(percent)은 %p 차이, 나머지는 증감률(%). 지난달이 0이면 0"""
    if unit == "percent":
        return round(current - previous, 1)
    return percent_change(current, previous) if previous else 0.0


def _kpi(
    key: Literal["revenue", "orders", "signups", "conversion"],
    label: str,
    unit: Literal["won", "count", "percent"],
    month: Pair,
    day_week: dict[ComparePeriod, Pair] | None = None,
) -> Kpi:
    """이번 달 값·지난달 대비 증감과 전일·지난주·지난달 비교를 한 번에 만든다."""
    current, previous = month
    comparisons = [
        KpiComparison(period=period, current=c, previous=p)
        for period, (c, p) in (day_week or {}).items()
    ]
    comparisons.append(
        KpiComparison(period="month", current=current, previous=previous)
    )
    return Kpi(
        key=key,
        label=label,
        value=current,
        unit=unit,
        change=_change(current, previous, unit),
        comparisons=comparisons,
    )


def _pair[T](current: T | None, previous: T | None, get: Callable[[T], float]) -> Pair:
    """두 행에서 같은 값을 꺼낸다. 행이 없으면 0"""
    return (get(current) if current else 0, get(previous) if previous else 0)


def _average[T](rows: list[T], get: Callable[[T], float]) -> float:
    return round(sum(get(row) for row in rows) / len(rows), 2) if rows else 0.0


async def get_kpis(session: AsyncSession) -> list[Kpi]:
    today = clock.now().date()
    this_ym, last_ym = year_month(today), year_month(today, 1)
    monthly = await stats_crud.get_monthly_metrics(session, [this_ym, last_ym])
    this_month, last_month = monthly.get(this_ym), monthly.get(last_ym)

    # 오늘부터 13일 전까지 최신순. 없는 날은 None
    daily = await stats_crud.get_daily_metrics(
        session, today - timedelta(days=13), today
    )
    days = [daily.get(today - timedelta(days=i)) for i in range(14)]
    week = [d for d in days[:7] if d]
    prev_week = [d for d in days[7:] if d]

    def month(get: Callable[[MonthlyMetric], float]) -> Pair:
        return _pair(this_month, last_month, get)

    # 전일: 오늘 vs 어제 / 지난주: 최근 7일(오늘 포함) 합 vs 그 전 7일 합
    def day_week(get: Callable[[DailyMetric], int]) -> dict[ComparePeriod, Pair]:
        return {
            "day": _pair(days[0], days[1], get),
            "week": (sum(map(get, week)), sum(map(get, prev_week))),
        }

    def daily_rate(d: DailyMetric) -> float:
        return float(d.conversion_rate)

    # 전환율의 지난주 비교는 7일 평균
    conversion: dict[ComparePeriod, Pair] = {
        "day": _pair(days[0], days[1], daily_rate),
        "week": (_average(week, daily_rate), _average(prev_week, daily_rate)),
    }

    return [
        _kpi("revenue", "매출", "won", month(lambda m: m.revenue)),
        _kpi(
            "orders",
            "주문 수",
            "count",
            month(lambda m: m.orders),
            day_week(lambda d: d.orders),
        ),
        _kpi(
            "signups",
            "신규 가입자",
            "count",
            month(lambda m: m.signups),
            day_week(lambda d: d.signups),
        ),
        _kpi(
            "conversion",
            "전환율",
            "percent",
            month(lambda m: float(m.conversion_rate)),
            conversion,
        ),
    ]


async def get_revenue_trend(session: AsyncSession) -> RevenueTrend:
    today = clock.now().date()
    # 최근 12개월(오래된 순)과 전년 동월(12개월 전)
    months = [year_month(today, months_ago) for months_ago in range(11, -1, -1)]
    last_year = year_month(today, 12)
    monthly = await stats_crud.get_monthly_metrics(session, [last_year, *months])
    rows = [monthly.get(ym) for ym in months]
    return RevenueTrend(
        months=[f"{int(ym[5:])}월" for ym in months],
        revenue=[row.revenue if row else 0 for row in rows],
        orders=[row.orders if row else 0 for row in rows],
        last_year_same_month_revenue=(
            monthly[last_year].revenue if last_year in monthly else 0
        ),
    )


async def get_category_shares(session: AsyncSession) -> list[CategoryShare]:
    rows = await stats_crud.list_category_sales(session, year_month(clock.now().date()))
    return [CategoryShare(name=row.category, value=row.revenue) for row in rows]


async def get_traffic_sources(session: AsyncSession) -> list[TrafficSource]:
    rows = await stats_crud.list_traffic_sources(
        session, year_month(clock.now().date())
    )
    return [TrafficSource(channel=row.channel, visitors=row.visitors) for row in rows]


async def get_hourly_traffic(session: AsyncSession) -> HourlyTraffic:
    rows = await stats_crud.list_hourly_visits(session)
    return HourlyTraffic(
        days=DAYS,
        hours=HOURS,
        values=[(row.hour, row.weekday, row.visits) for row in rows],
    )


async def get_recent_orders(session: AsyncSession) -> list[RecentOrder]:
    orders = await order_crud.list_recent(session, RECENT_ORDERS_LIMIT)
    return [
        RecentOrder.model_validate(
            {
                "id": order.order_no,
                "customer": order.customer.name,
                "amount": order.amount,
                "status": order.status,
                "ordered_at": order.ordered_at,
            }
        )
        for order in orders
    ]


async def get_todos(session: AsyncSession) -> TodoSummary:
    status_counts = await order_crud.count_by_status(
        session, ["paid", "refund_requested"]
    )
    low_stock = await product_crud.count_low_stock(session, LOW_STOCK_THRESHOLD)
    pending_inquiries = await inquiry_crud.count_by_status(session, "pending")
    done_today = await stats_crud.get_todos_done(session, clock.now().date())
    return TodoSummary(
        items=[
            TodoItem(
                key="pending-orders",
                label="발송 대기 주문",
                count=status_counts.get("paid", 0),
                unit="건",
                href="/admin/orders",
                urgent=True,
            ),
            TodoItem(
                key="refunds",
                label="환불 요청",
                count=status_counts.get("refund_requested", 0),
                unit="건",
                href="/admin/orders",
                urgent=True,
            ),
            TodoItem(
                key="low-stock",
                label="재고 부족 상품",
                count=low_stock,
                unit="개",
                href="/admin/products",
            ),
            TodoItem(
                key="inquiries",
                label="답변 대기 회원 문의",
                count=pending_inquiries,
                unit="건",
                href="/admin/users",
            ),
        ],
        done_today=done_today,
    )


async def get_today_revenue(session: AsyncSession) -> TodayRevenue:
    # now 를 한 번만 읽어서 "오늘 0시"와 "지금"이 같은 기준이 되게 한다
    now = clock.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    one_day = timedelta(days=1)
    return TodayRevenue(
        today=await order_crud.sum_amount(session, today, now),
        yesterday_same_time=await order_crud.sum_amount(
            session, today - one_day, now - one_day
        ),
    )
