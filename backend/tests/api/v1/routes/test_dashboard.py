import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

BASE = f"{settings.API_PREFIX}/v1/dashboard"


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
def test_endpoints_ok(client: TestClient, path: str) -> None:
    assert client.get(f"{BASE}/{path}").status_code == 200


def test_keys_are_camel_case(client: TestClient) -> None:
    assert "lastYearSameMonthRevenue" in client.get(f"{BASE}/revenue-trend").json()
    assert "orderedAt" in client.get(f"{BASE}/recent-orders").json()[0]
    assert "doneToday" in client.get(f"{BASE}/todos").json()
    assert "yesterdaySameTime" in client.get(f"{BASE}/today-revenue").json()


def test_kpis_computed_from_revenue_trend(client: TestClient) -> None:
    kpis = {k["key"]: k for k in client.get(f"{BASE}/kpis").json()}
    assert kpis["revenue"]["value"] == 128_450_000
    assert kpis["revenue"]["change"] == 5.9
    assert kpis["orders"]["value"] == 3842
    assert kpis["orders"]["change"] == 8.2


def test_hourly_traffic_shape(client: TestClient) -> None:
    data = client.get(f"{BASE}/hourly-traffic").json()
    assert len(data["days"]) == 7
    assert len(data["hours"]) == 24
    assert len(data["values"]) == 168
    # JS 와 같은 순서: 요일 바깥, 시간 안쪽
    assert data["values"][0][:2] == [0, 0]
    assert data["values"][1][:2] == [1, 0]
    assert data["values"][24][:2] == [0, 1]


def test_ordered_at_is_seoul_time(client: TestClient) -> None:
    orders = client.get(f"{BASE}/recent-orders").json()
    assert orders[0]["orderedAt"] == "2026-09-30T13:42:00+09:00"
    assert all(o["orderedAt"].endswith("+09:00") for o in orders)


def test_todo_urgent_defaults_to_false(client: TestClient) -> None:
    items = {i["key"]: i for i in client.get(f"{BASE}/todos").json()["items"]}
    assert items["pending-orders"]["urgent"] is True
    assert items["low-stock"]["urgent"] is False
