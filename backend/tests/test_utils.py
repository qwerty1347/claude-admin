import pytest

from app.utils import percent_change, round_half_up


@pytest.mark.parametrize(
    ("x", "expected"),
    [(2.5, 3), (3.5, 4), (2.4, 2), (0.5, 1), (10.0, 10)],
)
def test_round_half_up(x: float, expected: int) -> None:
    assert round_half_up(x) == expected


def test_round_half_up_differs_from_builtin_round() -> None:
    assert round(2.5) == 2
    assert round_half_up(2.5) == 3


def test_percent_change_increase() -> None:
    # 대시보드 매출: 8월 121,300,000 → 9월 128,450,000
    assert percent_change(128_450_000, 121_300_000) == 5.9


def test_percent_change_decrease() -> None:
    assert percent_change(90, 100) == -10.0


def test_percent_change_previous_zero() -> None:
    with pytest.raises(ValueError):
        percent_change(10, 0)
