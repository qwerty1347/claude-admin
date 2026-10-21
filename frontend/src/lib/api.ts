// 대시보드 데이터 접근 계층. 컴포넌트는 이 파일의 함수만 호출한다.
// API_URL 이 있으면 백엔드(FastAPI)를 호출하고, 없으면 mock 데이터를 반환한다.
// 백엔드 응답 틀({ statusCode, code, data })은 request() 에서만 풀고, 컴포넌트는 데이터만 받는다.
import { unstable_rethrow } from "next/navigation";
import { cache } from "react";
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
import type { ApiErrorBody, ApiResponse, FieldError } from "@/types/api";
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

/** 백엔드가 실패 응답을 줬거나 응답하지 않았을 때 */
export class ApiRequestError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly errors: FieldError[] = [],
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.name = "ApiRequestError";
  }
}

const TIMEOUT_MS = 5_000;

async function request<T>(path: string, fallback: T): Promise<T> {
  const baseUrl = process.env.API_URL;
  if (!baseUrl) return fallback;

  let res: Response;
  try {
    res = await fetch(`${baseUrl}/api/v1${path}`, {
      // cacheComponents 가 꺼져 있으면 옵션 없는 fetch 는 next build 때 한 번 실행돼 값이 굳는다
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (e) {
    // Next 내부 신호(예: 빌드 중 no-store fetch → "동적 렌더링으로 전환")는 삼키지 않고 그대로 넘긴다
    unstable_rethrow(e);
    // 연결 실패·타임아웃
    throw new ApiRequestError(0, "NETWORK_ERROR", `백엔드에 연결하지 못했어요 (${path})`, [], { cause: e });
  }

  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new ApiRequestError(
      res.status,
      body?.code ?? "UNKNOWN_ERROR",
      body?.message ?? `요청에 실패했어요 (${res.status} ${path})`,
      body?.errors ?? [],
    );
  }

  const body = (await res.json()) as ApiResponse<T>;
  return body.data;
}

export function getKpis(): Promise<Kpi[]> {
  return request("/dashboard/kpis", kpis);
}

export function getRevenueTrend(): Promise<RevenueTrend> {
  return request("/dashboard/revenue-trend", revenueTrend);
}

export function getCategoryShares(): Promise<CategoryShare[]> {
  return request("/dashboard/category-shares", categoryShares);
}

export function getTrafficSources(): Promise<TrafficSource[]> {
  return request("/dashboard/traffic-sources", trafficSources);
}

export function getHourlyTraffic(): Promise<HourlyTraffic> {
  return request("/dashboard/hourly-traffic", hourlyTraffic);
}

export function getRecentOrders(): Promise<Order[]> {
  return request("/dashboard/recent-orders", recentOrders);
}

// 레이아웃(사이드바 배지)과 페이지가 함께 호출하므로 한 요청 안에서는 한 번만 부른다.
// fetch 자동 중복 제거는 signal 옵션 때문에 적용되지 않아 React.cache 로 묶는다.
export const getTodos = cache(
  (): Promise<TodoSummary> => request("/dashboard/todos", { items: todos, doneToday: todoDoneToday }),
);

export function getTodayRevenue(): Promise<TodayRevenue> {
  return request("/dashboard/today-revenue", todayRevenue);
}

/** 사이드바 메뉴 옆에 표시할 처리 대기 건수 (메뉴 href → 건수). todos 에서 계산한다. */
export async function getNavBadges(): Promise<Record<string, number>> {
  const { items } = await getTodos();
  const badges: Record<string, number> = {};
  for (const todo of items) {
    if (todo.urgent) badges[todo.href] = (badges[todo.href] ?? 0) + todo.count;
  }
  return badges;
}
