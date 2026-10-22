"""
- 두 곳 이상에서 쓰는 함수만 둔다. 한 기능에서만 쓰는 함수는 그 기능 근처(crud/<도메인>.py 등)에 둔다.
- 설정·시간·보안·DB 같은 앱 기반 기능은 app/core/ 에 둔다. (현재 시각: app/core/clock.py)
- 화면 표시용 포맷(원화, 조사 등)은 프론트 src/lib/format.ts 담당이다. 백엔드는 원래 값을 내려준다.
"""

import math
from datetime import date


def round_half_up(x: float) -> int:
    """0.5는 올림. JS Math.round와 같은 결과 (2.5 → 3).

    Python 내장 round()는 짝수 쪽으로 반올림한다 (round(2.5) == 2).
    """
    return math.floor(x + 0.5)


def percent_change(current: float, previous: float, ndigits: int = 1) -> float:
    """previous 대비 current 증감률(%). 예: percent_change(110, 100) == 10.0

    previous가 0이면 증감률을 정의할 수 없으므로 ValueError. 표시 방법은 호출하는 쪽이 정한다.
    """
    if previous == 0:
        raise ValueError("previous must not be 0")
    return round((current - previous) / previous * 100, ndigits)


def year_month(day: date, months_ago: int = 0) -> str:
    """day 가 속한 달에서 months_ago 개월 전의 "YYYY-MM". 예: year_month(date(2026, 1, 5), 1) == "2025-12" """
    index = day.year * 12 + day.month - 1 - months_ago
    return f"{index // 12}-{index % 12 + 1:02d}"
