import type {
  CategoryShare,
  HourlyTraffic,
  Kpi,
  Order,
  RevenueTrend,
  TodayRevenue,
  TodoItem,
  TrafficSource,
} from "@/types/dashboard";

// backend/app/crud/dashboard.py 의 get_kpis() 와 같은 값 (API_URL 없을 때 대체용)
export const kpis: Kpi[] = [
  {
    key: "revenue",
    label: "매출",
    value: 128_450_000,
    unit: "won",
    change: 5.9,
    comparisons: [{ period: "month", current: 128_450_000, previous: 121_300_000 }],
  },
  {
    key: "orders",
    label: "주문 수",
    value: 3_842,
    unit: "count",
    change: 8.2,
    comparisons: [
      { period: "day", current: 118, previous: 109 },
      { period: "week", current: 862, previous: 905 },
      { period: "month", current: 3_842, previous: 3_550 },
    ],
  },
  {
    key: "signups",
    label: "신규 가입자",
    value: 1_216,
    unit: "count",
    change: -3.2,
    comparisons: [
      { period: "day", current: 37, previous: 41 },
      { period: "week", current: 281, previous: 264 },
      { period: "month", current: 1_216, previous: 1_256 },
    ],
  },
  {
    key: "conversion",
    label: "전환율",
    value: 3.46,
    unit: "percent",
    change: 0.4,
    comparisons: [
      { period: "day", current: 3.62, previous: 3.41 },
      { period: "week", current: 3.51, previous: 3.58 },
      { period: "month", current: 3.46, previous: 3.06 },
    ],
  },
];

export const revenueTrend: RevenueTrend = {
  // 최근 12개월 (작년 10월 ~ 이번 달 9월)
  months: ["10월", "11월", "12월", "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월"],
  revenue: [
    82_000_000, 76_500_000, 91_200_000, 88_700_000, 97_300_000, 104_800_000,
    99_100_000, 108_600_000, 114_200_000, 110_900_000, 121_300_000, 128_450_000,
  ],
  orders: [2410, 2280, 2690, 2610, 2870, 3050, 2940, 3180, 3320, 3260, 3550, 3842],
  // 작년 9월
  lastYearSameMonthRevenue: 104_300_000,
};

export const categoryShares: CategoryShare[] = [
  { name: "의류", value: 38_200_000 },
  { name: "전자기기", value: 31_600_000 },
  { name: "뷰티", value: 21_400_000 },
  { name: "식품", value: 17_900_000 },
  { name: "생활용품", value: 12_150_000 },
  { name: "기타", value: 7_200_000 },
];

export const trafficSources: TrafficSource[] = [
  { channel: "검색 (Organic)", visitors: 48_320 },
  { channel: "직접 방문", visitors: 31_870 },
  { channel: "SNS", visitors: 24_510 },
  { channel: "광고 (Paid)", visitors: 18_940 },
  { channel: "이메일", visitors: 9_280 },
  { channel: "추천 (Referral)", visitors: 6_150 },
];

const days = ["월", "화", "수", "목", "금", "토", "일"];
const hours = Array.from({ length: 24 }, (_, h) => `${h}시`);

// 결정적인 값(매 렌더마다 동일)으로 만들어 hydration 불일치를 피한다.
function hourlyValue(hour: number, day: number): number {
  const daytime = Math.max(0, Math.sin(((hour - 6) / 24) * Math.PI * 2)) * 80;
  const evening = hour >= 19 && hour <= 23 ? 45 : 0;
  const weekend = day >= 5 ? 25 : 0;
  const noise = ((hour * 7 + day * 13) % 11) * 2;
  return Math.round(10 + daytime + evening + weekend + noise);
}

export const hourlyTraffic: HourlyTraffic = {
  days,
  hours,
  values: days.flatMap((_, d) =>
    hours.map((_, h) => [h, d, hourlyValue(h, d)] as [number, number, number]),
  ),
};

export const recentOrders: Order[] = [
  { id: "ORD-260930-1042", customer: "김민준", amount: 128_000, status: "paid", orderedAt: "2026-09-30T13:42:00+09:00" },
  { id: "ORD-260930-1041", customer: "이서연", amount: 54_900, status: "shipping", orderedAt: "2026-09-30T13:15:00+09:00" },
  { id: "ORD-260930-1040", customer: "박지훈", amount: 312_500, status: "delivered", orderedAt: "2026-09-30T12:58:00+09:00" },
  { id: "ORD-260930-1039", customer: "최수아", amount: 19_800, status: "cancelled", orderedAt: "2026-09-30T12:31:00+09:00" },
  { id: "ORD-260930-1038", customer: "정도윤", amount: 87_300, status: "paid", orderedAt: "2026-09-30T11:47:00+09:00" },
  { id: "ORD-260930-1037", customer: "강하은", amount: 243_000, status: "shipping", orderedAt: "2026-09-30T11:09:00+09:00" },
  { id: "ORD-260930-1036", customer: "윤시우", amount: 66_400, status: "delivered", orderedAt: "2026-09-30T10:22:00+09:00" },
];

export const todos: TodoItem[] = [
  { key: "pending-orders", label: "발송 대기 주문", count: 12, unit: "건", href: "/admin/orders", urgent: true },
  { key: "refunds", label: "환불 요청", count: 2, unit: "건", href: "/admin/orders", urgent: true },
  { key: "low-stock", label: "재고 부족 상품", count: 3, unit: "개", href: "/admin/products" },
  { key: "inquiries", label: "답변 대기 회원 문의", count: 5, unit: "건", href: "/admin/users" },
];

export const todoDoneToday = 23;

export const todayRevenue: TodayRevenue = {
  today: 4_120_000,
  yesterdaySameTime: 3_810_000,
};
