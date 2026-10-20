from datetime import timedelta

from app.core.clock import now, start_of_today, utcnow


def test_now_is_seoul_time() -> None:
    assert now().utcoffset() == timedelta(hours=9)
    assert now().isoformat().endswith("+09:00")


def test_utcnow_is_utc() -> None:
    assert utcnow().utcoffset() == timedelta(0)


def test_now_and_utcnow_are_same_instant() -> None:
    # 타임존이 붙은 datetime은 표시 시간대가 달라도 같은 순간이면 비교가 맞다
    assert abs(now() - utcnow()) < timedelta(seconds=1)


def test_start_of_today_is_seoul_midnight() -> None:
    start = start_of_today()
    assert (start.hour, start.minute, start.second, start.microsecond) == (0, 0, 0, 0)
    assert start.utcoffset() == timedelta(hours=9)
    assert start.date() == now().date()
