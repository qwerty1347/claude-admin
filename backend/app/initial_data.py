"""대시보드 시드 데이터. 실행: uv run python -m app.initial_data

mock(2026-09-30 13:50 기준 스냅샷)의 숫자를 기준 시각 now 에 맞춰 상대 날짜로 넣는다.
- 실행할 때는 clock.now(), 테스트할 때는 고정 시각을 넣는다.
- 시드 대상 테이블을 비우고 다시 넣으므로 여러 번 실행해도 결과가 같다.
- commit 은 호출하는 쪽이 한다.
"""

import logging
import math
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core import clock
from app.core.config import settings
from app.core.db import SessionLocal
from app.models import (
    Customer,
    DailyMetric,
    HourlyVisit,
    Inquiry,
    MonthlyCategorySale,
    MonthlyMetric,
    MonthlyTrafficSource,
    Order,
    OrderStatus,
    Product,
)
from app.utils import round_half_up

logger = logging.getLogger(__name__)

# 월별: 11개월 전 ~ 이번 달 (12개)
MONTHLY_REVENUE = [
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
]
MONTHLY_ORDERS = [
    2410,
    2280,
    2690,
    2610,
    2870,
    3050,
    2940,
    3180,
    3320,
    3260,
    3550,
    3842,
]
# 이번 달·지난달(1,216/1,256, 3.46/3.06)만 화면에 쓰인다. 나머지는 그럴듯한 값
MONTHLY_SIGNUPS = [980, 925, 1043, 1010, 1088, 1135, 1102, 1164, 1198, 1181, 1256, 1216]
MONTHLY_CONVERSION = [
    "2.94",
    "2.87",
    "3.12",
    "3.05",
    "3.18",
    "3.27",
    "3.21",
    "3.30",
    "3.38",
    "3.33",
    "3.06",
    "3.46",
]
# 전년 동월(12개월 전). 화면에는 매출만 쓰인다
LAST_YEAR_SAME_MONTH = {
    "revenue": 104_300_000,
    "orders": 3010,
    "signups": 1050,
    "conversion_rate": Decimal("3.15"),
}

CATEGORY_SALES = [
    ("의류", 38_200_000),
    ("전자기기", 31_600_000),
    ("뷰티", 21_400_000),
    ("식품", 17_900_000),
    ("생활용품", 12_150_000),
    ("기타", 7_200_000),
]

TRAFFIC_SOURCES = [
    ("검색 (Organic)", 48_320),
    ("직접 방문", 31_870),
    ("SNS", 24_510),
    ("광고 (Paid)", 18_940),
    ("이메일", 9_280),
    ("추천 (Referral)", 6_150),
]

# 일별: (오늘, 어제)와 (최근 7일 합, 그 전 7일 합). 전환율은 7일 평균
DAILY_ORDERS = (118, 109)
WEEKLY_ORDERS = (862, 905)
DAILY_SIGNUPS = (37, 41)
WEEKLY_SIGNUPS = (281, 264)
DAILY_CONVERSION = (Decimal("3.62"), Decimal("3.41"))
WEEKLY_CONVERSION = (Decimal("3.51"), Decimal("3.58"))
TODOS_DONE_TODAY = 23
TODOS_DONE_OTHER_DAYS = 20

# 최근 주문 7건: (주문 번호 끝자리, 고객, 금액, 상태, now 몇 분 전)
# mock 시각(13:42 ~ 10:22)을 13:50 기준으로 바꾼 값. 기준 시각보다 미래 주문이 생기지 않게 상대 시간으로 둔다
RECENT_ORDERS: list[tuple[int, str, int, OrderStatus, int]] = [
    (1042, "김민준", 128_000, "paid", 8),
    (1041, "이서연", 54_900, "shipping", 35),
    (1040, "박지훈", 312_500, "delivered", 52),
    (1039, "최수아", 19_800, "cancelled", 79),
    (1038, "정도윤", 87_300, "paid", 123),
    (1037, "강하은", 243_000, "shipping", 161),
    (1036, "윤시우", 66_400, "delivered", 208),
]

# 오늘 보충 주문 19건 (1017 ~ 1035, 오래된 순). 최근 7건과 합쳐 오늘 매출 4,120,000
TODAY_EXTRA_AMOUNTS = [
    45_000,
    129_000,
    78_500,
    210_000,
    33_900,
    156_000,
    89_000,
    264_000,
    52_800,
    198_000,
    71_200,
    345_000,
    118_000,
    61_700,
    412_000,
    287_500,
    199_000,
    305_000,
    152_500,
]
# 앞 9건은 발송됨, 뒤 10건은 발송 대기. 최근 7건의 paid 2건과 합쳐 paid 12건
TODAY_EXTRA_SHIPPED = 9

# 어제 같은 시각까지의 주문 19건 (1001 ~ 1019). 합계 3,810,000
YESTERDAY_AMOUNTS = [
    98_000,
    245_000,
    56_700,
    187_000,
    132_500,
    310_000,
    74_900,
    229_000,
    158_000,
    420_000,
    63_400,
    276_000,
    189_500,
    91_000,
    352_000,
    118_000,
    205_000,
    403_000,
    201_000,
]
# 어제 주문 중 상태가 delivered 가 아닌 것 (index: 상태). refund_requested 2건
YESTERDAY_STATUS: dict[int, OrderStatus] = {
    3: "refund_requested",
    7: "cancelled",
    11: "refund_requested",
}

TODAY_REVENUE = 4_120_000
YESTERDAY_SAME_TIME_REVENUE = 3_810_000
assert sum(o[2] for o in RECENT_ORDERS) + sum(TODAY_EXTRA_AMOUNTS) == TODAY_REVENUE
assert sum(YESTERDAY_AMOUNTS) == YESTERDAY_SAME_TIME_REVENUE

SHIP_DELAY = timedelta(minutes=30)
SHIPPED_STATUSES = {"shipping", "delivered", "refund_requested"}

# 최근 주문 고객 7명 + 보충 주문·문의용 고객
CUSTOMER_NAMES = [
    *(o[1] for o in RECENT_ORDERS),
    "임서준",
    "송예린",
    "조하준",
    "신유나",
    "권도현",
    "황지아",
    "안준서",
    "배수빈",
    "전예준",
    "홍채원",
    "문시윤",
    "양지호",
    "손하린",
]

# (이름, 카테고리, 재고). 재고 10개 미만 3개
PRODUCTS = [
    ("오버핏 코튼 셔츠", "의류", 42),
    ("와이드 데님 팬츠", "의류", 7),
    ("무선 이어폰", "전자기기", 65),
    ("보조배터리 10000mAh", "전자기기", 4),
    ("수분 크림", "뷰티", 88),
    ("선크림 SPF50", "뷰티", 9),
    ("그래놀라 500g", "식품", 120),
    ("드립백 커피 세트", "식품", 54),
    ("극세사 수건 5장", "생활용품", 73),
    ("디퓨저 200ml", "생활용품", 31),
]

# 문의 (now 몇 시간 전, 상태). 답변 대기 5건
INQUIRIES = [
    (1, "pending"),
    (3, "pending"),
    (6, "pending"),
    (20, "pending"),
    (26, "pending"),
    (30, "answered"),
    (48, "answered"),
    (72, "answered"),
]

# FK 때문에 자식 테이블부터 지운다
SEED_MODELS = [
    Order,
    Inquiry,
    Customer,
    Product,
    MonthlyMetric,
    MonthlyCategorySale,
    MonthlyTrafficSource,
    HourlyVisit,
    DailyMetric,
]


def _year_month(day: date, months_ago: int) -> str:
    """day 가 속한 달에서 months_ago 개월 전. 예: _year_month(date(2026, 1, 5), 1) == "2025-12" """
    index = day.year * 12 + day.month - 1 - months_ago
    return f"{index // 12}-{index % 12 + 1:02d}"


def _spread(total: int, n: int) -> list[int]:
    """total 을 n 개로 최대한 고르게 나눈다. 예: _spread(10, 3) == [4, 3, 3]"""
    base, extra = divmod(total, n)
    return [base + 1 if i < extra else base for i in range(n)]


def _last_14_days(daily: tuple[int, int], weekly: tuple[int, int]) -> list[int]:
    """오늘부터 13일 전까지 14일치 값 (최신순). 앞 7일 합은 weekly[0], 뒤 7일 합은 weekly[1]"""
    today, yesterday = daily
    week, prev_week = weekly
    return [
        today,
        yesterday,
        *_spread(week - today - yesterday, 5),
        *_spread(prev_week, 7),
    ]


def _last_14_days_rate(
    daily: tuple[Decimal, Decimal], weekly: tuple[Decimal, Decimal]
) -> list[Decimal]:
    """전환율 버전. 0.01 단위 정수로 나눈 뒤 되돌린다 (7일 평균이 weekly 가 되게)"""
    values = _last_14_days(
        (int(daily[0] * 100), int(daily[1] * 100)),
        (int(weekly[0] * 7 * 100), int(weekly[1] * 7 * 100)),
    )
    return [Decimal(v) / 100 for v in values]


def _between(start: datetime, end: datetime, n: int) -> list[datetime]:
    """start 와 end 사이(양 끝 제외)에 n 개 시각을 고르게 둔다. 분 단위로 자른다"""
    step = (end - start) / (n + 1)
    return [(start + step * (i + 1)).replace(second=0, microsecond=0) for i in range(n)]


def _hourly_value(hour: int, day: int) -> int:
    # mock-data.ts 의 hourlyValue 와 같은 식. 반올림도 JS Math.round 와 같게 맞춘다.
    daytime = max(0.0, math.sin((hour - 6) / 24 * math.pi * 2)) * 80
    evening = 45 if 19 <= hour <= 23 else 0
    weekend = 25 if day >= 5 else 0
    noise = ((hour * 7 + day * 13) % 11) * 2
    return round_half_up(10 + daytime + evening + weekend + noise)


def _order(
    no: str, customer_id: int, amount: int, status: OrderStatus, ordered_at: datetime
) -> Order:
    return Order(
        order_no=no,
        customer_id=customer_id,
        amount=amount,
        status=status,
        ordered_at=ordered_at,
        shipped_at=ordered_at + SHIP_DELAY if status in SHIPPED_STATUSES else None,
    )


def _build_orders(now: datetime, customer_ids: dict[str, int]) -> list[Order]:
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    today_no = f"ORD-{today:%y%m%d}"
    yesterday_no = f"ORD-{yesterday:%y%m%d}"
    # 보충 주문 고객은 최근 주문 고객이 아닌 사람들로 돌아가며 정한다
    others = [customer_ids[name] for name in CUSTOMER_NAMES[len(RECENT_ORDERS) :]]

    orders = [
        _order(
            f"{today_no}-{seq}",
            customer_ids[name],
            amount,
            status,
            now - timedelta(minutes=minutes_ago),
        )
        for seq, name, amount, status, minutes_ago in RECENT_ORDERS
    ]

    # 오늘 0시 ~ 최근 7건 중 가장 오래된 주문 사이
    earliest_recent = now - timedelta(minutes=RECENT_ORDERS[-1][4])
    for i, ordered_at in enumerate(
        _between(today, earliest_recent, len(TODAY_EXTRA_AMOUNTS))
    ):
        orders.append(
            _order(
                f"{today_no}-{1017 + i}",
                others[i % len(others)],
                TODAY_EXTRA_AMOUNTS[i],
                "shipping" if i < TODAY_EXTRA_SHIPPED else "paid",
                ordered_at,
            )
        )

    # 어제 0시 ~ 어제 같은 시각 사이
    for i, ordered_at in enumerate(
        _between(yesterday, now - timedelta(days=1), len(YESTERDAY_AMOUNTS))
    ):
        orders.append(
            _order(
                f"{yesterday_no}-{1001 + i}",
                others[(i + 5) % len(others)],
                YESTERDAY_AMOUNTS[i],
                YESTERDAY_STATUS.get(i, "delivered"),
                ordered_at,
            )
        )
    return orders


def _build_stats(
    now: datetime,
) -> list[
    MonthlyMetric
    | MonthlyCategorySale
    | MonthlyTrafficSource
    | HourlyVisit
    | DailyMetric
]:
    today = now.date()
    this_month = _year_month(today, 0)

    rows: list[
        MonthlyMetric
        | MonthlyCategorySale
        | MonthlyTrafficSource
        | HourlyVisit
        | DailyMetric
    ] = [
        MonthlyMetric(year_month=_year_month(today, 12), **LAST_YEAR_SAME_MONTH),
    ]
    for i in range(12):
        rows.append(
            MonthlyMetric(
                year_month=_year_month(today, 11 - i),
                revenue=MONTHLY_REVENUE[i],
                orders=MONTHLY_ORDERS[i],
                signups=MONTHLY_SIGNUPS[i],
                conversion_rate=Decimal(MONTHLY_CONVERSION[i]),
            )
        )

    rows += [
        MonthlyCategorySale(year_month=this_month, category=category, revenue=revenue)
        for category, revenue in CATEGORY_SALES
    ]
    rows += [
        MonthlyTrafficSource(
            year_month=this_month, channel=channel, visitors=visitors, sort_order=i
        )
        for i, (channel, visitors) in enumerate(TRAFFIC_SOURCES)
    ]
    rows += [
        HourlyVisit(weekday=d, hour=h, visits=_hourly_value(h, d))
        for d in range(7)
        for h in range(24)
    ]

    orders = _last_14_days(DAILY_ORDERS, WEEKLY_ORDERS)
    signups = _last_14_days(DAILY_SIGNUPS, WEEKLY_SIGNUPS)
    conversion = _last_14_days_rate(DAILY_CONVERSION, WEEKLY_CONVERSION)
    rows += [
        DailyMetric(
            day=today - timedelta(days=i),
            orders=orders[i],
            signups=signups[i],
            conversion_rate=conversion[i],
            todos_done=TODOS_DONE_TODAY if i == 0 else TODOS_DONE_OTHER_DAYS,
        )
        for i in range(14)
    ]
    return rows


def seed(session: Session, now: datetime) -> None:
    """시드 대상 테이블을 비우고 now 기준 데이터를 넣는다. commit 은 하지 않는다."""
    now = now.astimezone(settings.tz)

    for model in SEED_MODELS:
        session.execute(delete(model))

    customers = [
        Customer(name=name, created_at=now - timedelta(days=7 * (i + 1)))
        for i, name in enumerate(CUSTOMER_NAMES)
    ]
    session.add_all(customers)
    session.flush()  # 주문·문의에 넣을 customer.id 를 받아온다
    customer_ids = {c.name: c.id for c in customers}

    session.add_all(_build_orders(now, customer_ids))
    session.add_all(
        Inquiry(
            customer_id=customers[i % len(customers)].id,
            status=status,
            created_at=now - timedelta(hours=hours_ago),
        )
        for i, (hours_ago, status) in enumerate(INQUIRIES)
    )
    session.add_all(
        Product(name=name, category=category, stock=stock)
        for name, category, stock in PRODUCTS
    )
    session.add_all(_build_stats(now))
    session.flush()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    now = clock.now()
    logger.info("시드 시작 (기준 시각 %s)", now.isoformat(timespec="minutes"))
    with SessionLocal() as session:
        seed(session, now)
        session.commit()
    logger.info("시드 완료")


if __name__ == "__main__":
    main()
