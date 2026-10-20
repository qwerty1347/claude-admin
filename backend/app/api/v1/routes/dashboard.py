from fastapi import APIRouter

from app.crud import dashboard as dashboard_crud
from app.schemas import (
    ApiResponse,
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
def read_kpis() -> ApiResponse[list[Kpi]]:
    return ApiResponse(data=dashboard_crud.get_kpis())


@router.get("/revenue-trend")
def read_revenue_trend() -> ApiResponse[RevenueTrend]:
    return ApiResponse(data=dashboard_crud.get_revenue_trend())


@router.get("/category-shares")
def read_category_shares() -> ApiResponse[list[CategoryShare]]:
    return ApiResponse(data=dashboard_crud.get_category_shares())


@router.get("/traffic-sources")
def read_traffic_sources() -> ApiResponse[list[TrafficSource]]:
    return ApiResponse(data=dashboard_crud.get_traffic_sources())


@router.get("/hourly-traffic")
def read_hourly_traffic() -> ApiResponse[HourlyTraffic]:
    return ApiResponse(data=dashboard_crud.get_hourly_traffic())


@router.get("/recent-orders")
def read_recent_orders() -> ApiResponse[list[RecentOrder]]:
    return ApiResponse(data=dashboard_crud.get_recent_orders())


@router.get("/todos")
def read_todos() -> ApiResponse[TodoSummary]:
    return ApiResponse(data=dashboard_crud.get_todos())


@router.get("/today-revenue")
def read_today_revenue() -> ApiResponse[TodayRevenue]:
    return ApiResponse(data=dashboard_crud.get_today_revenue())
