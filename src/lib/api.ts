// 대시보드 데이터 접근 계층.
// 지금은 하드코딩된 mock 데이터를 반환한다. 백엔드 연동 시 이 파일의 함수 내부만
// fetch(`${process.env.API_URL}/...`) 로 교체하면 되고, 호출하는 컴포넌트는 바꿀 필요가 없다.
import {
  categoryShares,
  hourlyTraffic,
  kpis,
  recentOrders,
  revenueTrend,
  todayRevenue,
  todoDoneToday,
  todos,
  trafficSources,
} from "@/lib/mock-data";
import type {
  CategoryShare,
  HourlyTraffic,
  Kpi,
  Order,
  RevenueTrend,
  TodayRevenue,
  TodoSummary,
  TrafficSource,
} from "@/types/dashboard";

export async function getKpis(): Promise<Kpi[]> {
  return kpis;
}

export async function getRevenueTrend(): Promise<RevenueTrend> {
  return revenueTrend;
}

export async function getCategoryShares(): Promise<CategoryShare[]> {
  return categoryShares;
}

export async function getTrafficSources(): Promise<TrafficSource[]> {
  return trafficSources;
}

export async function getHourlyTraffic(): Promise<HourlyTraffic> {
  return hourlyTraffic;
}

export async function getRecentOrders(): Promise<Order[]> {
  return recentOrders;
}

export async function getTodos(): Promise<TodoSummary> {
  return { items: todos, doneToday: todoDoneToday };
}

export async function getTodayRevenue(): Promise<TodayRevenue> {
  return todayRevenue;
}

/** 사이드바 메뉴 옆에 표시할 처리 대기 건수 (메뉴 href → 건수) */
export async function getNavBadges(): Promise<Record<string, number>> {
  const badges: Record<string, number> = {};
  for (const todo of todos) {
    if (todo.urgent) badges[todo.href] = (badges[todo.href] ?? 0) + todo.count;
  }
  return badges;
}
