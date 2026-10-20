"""현재 시각은 이 모듈을 통해서만 얻는다. datetime.now()를 직접 호출하지 않는다.

- utcnow(): 저장·기록용 (created_at, 로그 등)
- now():    업무 기준 시각용 ('오늘 0시' 경계, 화면에 보여줄 시각). settings.TIMEZONE 기준
"""

from datetime import UTC, datetime

from app.core.config import settings


def utcnow() -> datetime:
    return datetime.now(UTC)


def now() -> datetime:
    return datetime.now(settings.tz)


def start_of_today() -> datetime:
    """업무 시간대 기준 오늘 0시 (예: 2026-10-19 00:00:00+09:00)"""
    return now().replace(hour=0, minute=0, second=0, microsecond=0)
