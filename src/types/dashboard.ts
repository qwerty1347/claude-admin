export type Kpi = {
  key: "revenue" | "orders" | "signups" | "conversion";
  label: string;
  value: number;
  unit: "won" | "count" | "percent";
  /** 전기 대비 증감률 (%) */
  change: number;
};

export type RevenueTrend = {
  months: string[];
  revenue: number[];
  orders: number[];
  /** 작년 같은 달(이번 달의 1년 전) 매출 — 전년 동월 비교용 */
  lastYearSameMonthRevenue: number;
};

export type CategoryShare = {
  name: string;
  value: number;
};

export type TrafficSource = {
  channel: string;
  visitors: number;
};

export type HourlyTraffic = {
  days: string[];
  hours: string[];
  /** [hourIndex, dayIndex, value] */
  values: [number, number, number][];
};

export type OrderStatus = "paid" | "shipping" | "delivered" | "cancelled";

export type Order = {
  id: string;
  customer: string;
  amount: number;
  status: OrderStatus;
  /** ISO 8601, 타임존 포함. 예: "2026-09-30T13:42:00+09:00" (표시는 formatTime) */
  orderedAt: string;
};

export type TodoItem = {
  key: string;
  label: string;
  count: number;
  unit: "건" | "개";
  href: string;
  /** 바로 처리해야 하는 항목은 강조 */
  urgent?: boolean;
};

export type TodoSummary = {
  items: TodoItem[];
  /** 오늘 이미 처리한 건수 */
  doneToday: number;
};

export type TodayRevenue = {
  /** 오늘 0시부터 지금까지 매출 */
  today: number;
  /** 어제 0시부터 같은 시각까지 매출 */
  yesterdaySameTime: number;
};
