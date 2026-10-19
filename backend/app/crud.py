"""대시보드 조회 함수.

1단계는 DB 없이 mock 데이터를 반환한다 (src/lib/mock-data.ts 에서 옮김).
DB 를 붙이면 이 함수들의 내부만 바꾸고, 라우트와 응답 모델은 그대로 둔다.
"""

import math
from datetime import datetime

from app.core.config import settings
from app.models import (
    CategoryShare,
    HourlyTraffic,
    Kpi,
    RecentOrder,
    RevenueTrend,
    TodayRevenue,
    TodoItem,
    TodoSummary,
    TrafficSource,
)
from app.utils import percent_change, round_half_up

REVENUE_TREND = RevenueTrend(
    # 최근 12개월 (작년 10월 ~ 이번 달 9월)
    months=[
        "10월",
        "11월",
        "12월",
        "1월",
        "2월",
        "3월",
        "4월",
        "5월",
        "6월",
        "7월",
        "8월",
        "9월",
    ],
    revenue=[
        82_000_000,
        76_500_000,
        91_200_000,
        88_700_000,
        97_300_000,
        104_800_000,
        99_100_000,
        108_600_000,
        114_200_000,
        110_900_000,
        121_300_000,
        128_450_000,
    ],
    orders=[2410, 2280, 2690, 2610, 2870, 3050, 2940, 3180, 3320, 3260, 3550, 3842],
    # 작년 9월
    last_year_same_month_revenue=104_300_000,
)

CATEGORY_SHARES = [
    CategoryShare(name="의류", value=38_200_000),
    CategoryShare(name="전자기기", value=31_600_000),
    CategoryShare(name="뷰티", value=21_400_000),
    CategoryShare(name="식품", value=17_900_000),
    CategoryShare(name="생활용품", value=12_150_000),
    CategoryShare(name="기타", value=7_200_000),
]

TRAFFIC_SOURCES = [
    TrafficSource(channel="검색 (Organic)", visitors=48_320),
    TrafficSource(channel="직접 방문", visitors=31_870),
    TrafficSource(channel="SNS", visitors=24_510),
    TrafficSource(channel="광고 (Paid)", visitors=18_940),
    TrafficSource(channel="이메일", visitors=9_280),
    TrafficSource(channel="추천 (Referral)", visitors=6_150),
]

DAYS = ["월", "화", "수", "목", "금", "토", "일"]
HOURS = [f"{h}시" for h in range(24)]


def _order_time(hour: int, minute: int) -> datetime:
    return datetime(2026, 9, 30, hour, minute, tzinfo=settings.tz)


RECENT_ORDERS = [
    RecentOrder(
        id="ORD-260930-1042",
        customer="김민준",
        amount=128_000,
        status="paid",
        ordered_at=_order_time(13, 42),
    ),
    RecentOrder(
        id="ORD-260930-1041",
        customer="이서연",
        amount=54_900,
        status="shipping",
        ordered_at=_order_time(13, 15),
    ),
    RecentOrder(
        id="ORD-260930-1040",
        customer="박지훈",
        amount=312_500,
        status="delivered",
        ordered_at=_order_time(12, 58),
    ),
    RecentOrder(
        id="ORD-260930-1039",
        customer="최수아",
        amount=19_800,
        status="cancelled",
        ordered_at=_order_time(12, 31),
    ),
    RecentOrder(
        id="ORD-260930-1038",
        customer="정도윤",
        amount=87_300,
        status="paid",
        ordered_at=_order_time(11, 47),
    ),
    RecentOrder(
        id="ORD-260930-1037",
        customer="강하은",
        amount=243_000,
        status="shipping",
        ordered_at=_order_time(11, 9),
    ),
    RecentOrder(
        id="ORD-260930-1036",
        customer="윤시우",
        amount=66_400,
        status="delivered",
        ordered_at=_order_time(10, 22),
    ),
]

TODOS = [
    TodoItem(
        key="pending-orders",
        label="발송 대기 주문",
        count=12,
        unit="건",
        href="/admin/orders",
        urgent=True,
    ),
    TodoItem(
        key="refunds",
        label="환불 요청",
        count=2,
        unit="건",
        href="/admin/orders",
        urgent=True,
    ),
    TodoItem(
        key="low-stock",
        label="재고 부족 상품",
        count=3,
        unit="개",
        href="/admin/products",
    ),
    TodoItem(
        key="inquiries",
        label="답변 대기 회원 문의",
        count=5,
        unit="건",
        href="/admin/users",
    ),
]

TODO_DONE_TODAY = 23

TODAY_REVENUE = TodayRevenue(today=4_120_000, yesterday_same_time=3_810_000)


def get_kpis() -> list[Kpi]:
    # 매출·주문 수는 원천 데이터(REVENUE_TREND)에서 계산한다. 별도 숫자를 하드코딩하지 않는다.
    revenue, orders = REVENUE_TREND.revenue, REVENUE_TREND.orders
    return [
        Kpi(
            key="revenue",
            label="매출",
            value=revenue[-1],
            unit="won",
            change=percent_change(revenue[-1], revenue[-2]),
        ),
        Kpi(
            key="orders",
            label="주문 수",
            value=orders[-1],
            unit="count",
            change=percent_change(orders[-1], orders[-2]),
        ),
        # 신규 가입자·전환율은 원천 데이터가 없어 mock 값
        Kpi(key="signups", label="신규 가입자", value=1_216, unit="count", change=-3.2),
        Kpi(key="conversion", label="전환율", value=3.46, unit="percent", change=0.4),
    ]


def get_revenue_trend() -> RevenueTrend:
    return REVENUE_TREND


def get_category_shares() -> list[CategoryShare]:
    return CATEGORY_SHARES


def get_traffic_sources() -> list[TrafficSource]:
    return TRAFFIC_SOURCES


def _hourly_value(hour: int, day: int) -> int:
    # mock-data.ts 의 hourlyValue 와 같은 식. 반올림도 JS Math.round 와 같게 맞춘다.
    daytime = max(0.0, math.sin((hour - 6) / 24 * math.pi * 2)) * 80
    evening = 45 if 19 <= hour <= 23 else 0
    weekend = 25 if day >= 5 else 0
    noise = ((hour * 7 + day * 13) % 11) * 2
    return round_half_up(10 + daytime + evening + weekend + noise)


def get_hourly_traffic() -> HourlyTraffic:
    return HourlyTraffic(
        days=DAYS,
        hours=HOURS,
        values=[
            (h, d, _hourly_value(h, d))
            for d in range(len(DAYS))
            for h in range(len(HOURS))
        ],
    )


def get_recent_orders() -> list[RecentOrder]:
    return RECENT_ORDERS


def get_todos() -> TodoSummary:
    return TodoSummary(items=TODOS, done_today=TODO_DONE_TODAY)


def get_today_revenue() -> TodayRevenue:
    return TODAY_REVENUE
