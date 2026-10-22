from fastapi import APIRouter

from app.api.deps import AsyncSessionDep
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
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis")
async def read_kpis(session: AsyncSessionDep) -> ApiResponse[list[Kpi]]:
    return ApiResponse(data=await dashboard_service.get_kpis(session))


@router.get("/revenue-trend")
async def read_revenue_trend(session: AsyncSessionDep) -> ApiResponse[RevenueTrend]:
    return ApiResponse(data=await dashboard_service.get_revenue_trend(session))


@router.get("/category-shares")
async def read_category_shares(
    session: AsyncSessionDep,
) -> ApiResponse[list[CategoryShare]]:
    return ApiResponse(data=await dashboard_service.get_category_shares(session))


@router.get("/traffic-sources")
async def read_traffic_sources(
    session: AsyncSessionDep,
) -> ApiResponse[list[TrafficSource]]:
    return ApiResponse(data=await dashboard_service.get_traffic_sources(session))


@router.get("/hourly-traffic")
async def read_hourly_traffic(session: AsyncSessionDep) -> ApiResponse[HourlyTraffic]:
    return ApiResponse(data=await dashboard_service.get_hourly_traffic(session))


@router.get("/recent-orders")
async def read_recent_orders(
    session: AsyncSessionDep,
) -> ApiResponse[list[RecentOrder]]:
    return ApiResponse(data=await dashboard_service.get_recent_orders(session))


@router.get("/todos")
async def read_todos(session: AsyncSessionDep) -> ApiResponse[TodoSummary]:
    return ApiResponse(data=await dashboard_service.get_todos(session))


@router.get("/today-revenue")
async def read_today_revenue(session: AsyncSessionDep) -> ApiResponse[TodayRevenue]:
    return ApiResponse(data=await dashboard_service.get_today_revenue(session))
