from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

BASE = f"{settings.API_PREFIX}/v1/dashboard"


def get_data(client: TestClient, path: str) -> Any:
    """성공 응답 틀을 확인하고 data 만 꺼낸다."""
    r = client.get(f"{BASE}/{path}")
    assert r.status_code == 200
    body = r.json()
    assert body["statusCode"] == 200
    assert body["code"] == "OK"
    return body["data"]


@pytest.mark.parametrize(
    "path",
    [
        "kpis",
        "revenue-trend",
        "category-shares",
        "traffic-sources",
        "hourly-traffic",
        "recent-orders",
        "todos",
        "today-revenue",
    ],
)
def test_endpoints_return_success_envelope(client: TestClient, path: str) -> None:
    assert get_data(client, path) is not None


def test_keys_are_camel_case(client: TestClient) -> None:
    assert "lastYearSameMonthRevenue" in get_data(client, "revenue-trend")
    assert "orderedAt" in get_data(client, "recent-orders")[0]
    assert "doneToday" in get_data(client, "todos")
    assert "yesterdaySameTime" in get_data(client, "today-revenue")


def test_kpis_computed_from_revenue_trend(client: TestClient) -> None:
    kpis = {k["key"]: k for k in get_data(client, "kpis")}
    assert kpis["revenue"]["value"] == 128_450_000
    assert kpis["revenue"]["change"] == 5.9
    assert kpis["orders"]["value"] == 3842
    assert kpis["orders"]["change"] == 8.2


def test_kpi_comparisons(client: TestClient) -> None:
    kpis = {k["key"]: k for k in get_data(client, "kpis")}
    for key in ("orders", "signups", "conversion"):
        comps = {c["period"]: c for c in kpis[key]["comparisons"]}
        assert list(comps) == ["day", "week", "month"]
        # 지난달 비교의 이번 달 값 = KPI 값
        assert comps["month"]["current"] == kpis[key]["value"]
    assert kpis["orders"]["comparisons"][-1]["previous"] == 3550  # 매출 추이 8월
    # change 는 지난달 비교에서 계산 (count 는 %, percent 는 %p)
    assert kpis["signups"]["change"] == -3.2
    assert kpis["conversion"]["change"] == 0.4


def test_hourly_traffic_shape(client: TestClient) -> None:
    data = get_data(client, "hourly-traffic")
    assert len(data["days"]) == 7
    assert len(data["hours"]) == 24
    assert len(data["values"]) == 168
    # JS 와 같은 순서: 요일 바깥, 시간 안쪽
    assert data["values"][0][:2] == [0, 0]
    assert data["values"][1][:2] == [1, 0]
    assert data["values"][24][:2] == [0, 1]


def test_ordered_at_is_seoul_time(client: TestClient) -> None:
    orders = get_data(client, "recent-orders")
    assert orders[0]["orderedAt"] == "2026-09-30T13:42:00+09:00"
    assert all(o["orderedAt"].endswith("+09:00") for o in orders)


def test_todo_urgent_defaults_to_false(client: TestClient) -> None:
    items = {i["key"]: i for i in get_data(client, "todos")["items"]}
    assert items["pending-orders"]["urgent"] is True
    assert items["low-stock"]["urgent"] is False
