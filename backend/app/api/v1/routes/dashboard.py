from fastapi import APIRouter

from app import crud
from app.models import (
    CategoryShare,
    HourlyTraffic,
    Kpi,
    RecentOrder,
    RevenueTrend,
    TodayRevenue,
    TodoSummary,
    TrafficSource,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis")
def read_kpis() -> list[Kpi]:
    return crud.get_kpis()


@router.get("/revenue-trend")
def read_revenue_trend() -> RevenueTrend:
    return crud.get_revenue_trend()


@router.get("/category-shares")
def read_category_shares() -> list[CategoryShare]:
    return crud.get_category_shares()


@router.get("/traffic-sources")
def read_traffic_sources() -> list[TrafficSource]:
    return crud.get_traffic_sources()


@router.get("/hourly-traffic")
def read_hourly_traffic() -> HourlyTraffic:
    return crud.get_hourly_traffic()


@router.get("/recent-orders")
def read_recent_orders() -> list[RecentOrder]:
    return crud.get_recent_orders()


@router.get("/todos")
def read_todos() -> TodoSummary:
    return crud.get_todos()


@router.get("/today-revenue")
def read_today_revenue() -> TodayRevenue:
    return crud.get_today_revenue()
