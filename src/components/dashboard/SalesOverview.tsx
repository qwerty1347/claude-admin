"use client";

import { useMemo, useState } from "react";
import RevenueTrendChart from "@/components/charts/RevenueTrendChart";
import RollingTicker from "@/components/common/RollingTicker";
import Segmented from "@/components/common/Segmented";
import { formatNumber, formatPercent, formatWonKorean } from "@/lib/format";
import type { Kpi, RevenueTrend, TodayRevenue } from "@/types/dashboard";

type Range = "6" | "12";

const unitSuffix: Partial<Record<Kpi["key"], string>> = { orders: "건", signups: "명" };

function ChangeBadge({ change, unit }: { change: number; unit: Kpi["unit"] }) {
  const up = change >= 0;
  return (
    <span
      className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-[13px] font-semibold ${
        up ? "bg-[#ffeeee] text-rise" : "bg-primary-weak text-fall"
      }`}
    >
      {up ? "▲" : "▼"} {Math.abs(change).toFixed(1)}
      {unit === "percent" ? "%p" : "%"}
    </span>
  );
}

type Props = {
  kpis: Kpi[];
  trend: RevenueTrend;
  today: TodayRevenue;
};

export default function SalesOverview({ kpis, trend, today }: Props) {
  const [range, setRange] = useState<Range>("6");

  const others = kpis.filter((k) => k.key !== "revenue");

  // 이번 달 매출과 비교 기준은 모두 차트 데이터에서 계산해 숫자가 서로 어긋나지 않게 한다.
  const last = trend.revenue.length - 1;
  const current = trend.revenue[last];
  const compare = (value: number, base: number) => ({
    diff: value - base,
    change: ((value - base) / base) * 100,
  });

  const comparisons = [
    { label: "지난달보다", ...compare(current, trend.revenue[last - 1]) },
    { label: `작년 ${trend.months[last]}보다`, ...compare(current, trend.lastYearSameMonthRevenue) },
    {
      label: `오늘 ${formatWonKorean(today.today)}, 어제 이 시간보다`,
      ...compare(today.today, today.yesterdaySameTime),
    },
  ];

  const signedWon = (diff: number) => `${diff >= 0 ? "+" : "−"}${formatWonKorean(Math.abs(diff))}`;

  const visible = useMemo<RevenueTrend>(() => {
    const n = Number(range);
    return {
      ...trend,
      months: trend.months.slice(-n),
      revenue: trend.revenue.slice(-n),
      orders: trend.orders.slice(-n),
    };
  }, [trend, range]);

  return (
    <section className="flex h-full flex-col rounded-card bg-surface" aria-labelledby="sales-title">
      <div className="flex flex-wrap items-start justify-between gap-4 px-7 pt-7">
        <div>
          <h2 id="sales-title" className="text-[16px] font-semibold text-sub">
            {trend.months[last]} 매출
          </h2>
          <p className="mt-1 text-[40px] leading-tight font-bold tracking-tight text-ink">
            {formatWonKorean(current)}
          </p>
          <div className="mt-2">
            <RollingTicker
              srLabel="매출 비교"
              srItems={comparisons.map(
                (c) =>
                  `${c.label} ${Math.abs(c.change).toFixed(1)}% ${c.diff >= 0 ? "늘었어요" : "줄었어요"} (${signedWon(c.diff)})`,
              )}
              items={comparisons.map((c) => (
                <span key={c.label} className="flex items-center gap-2 text-[15px] whitespace-nowrap">
                  <span className="text-sub">{c.label}</span>
                  <ChangeBadge change={c.change} unit="won" />
                  <span className={`font-semibold ${c.diff >= 0 ? "text-rise" : "text-fall"}`}>
                    {signedWon(c.diff)}
                  </span>
                </span>
              ))}
            />
          </div>
        </div>
        <Segmented
          label="기간"
          value={range}
          onChange={setRange}
          options={[
            { value: "6", label: "6개월" },
            { value: "12", label: "12개월" },
          ]}
        />
      </div>

      <div className="flex-1 px-5 pt-4">
        <RevenueTrendChart data={visible} />
      </div>

      <dl className="grid grid-cols-1 border-t border-line sm:grid-cols-3">
        {others.map((kpi) => (
          <div
            key={kpi.key}
            className="border-line px-7 py-5 not-first:border-t sm:not-first:border-t-0 sm:not-first:border-l"
          >
            <dt className="text-[14px] text-muted">{kpi.label}</dt>
            <dd className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
              <span className="text-[22px] font-bold tracking-tight text-ink">
                {kpi.unit === "percent" ? formatPercent(kpi.value, 2) : formatNumber(kpi.value)}
                {unitSuffix[kpi.key] && (
                  <span className="ml-0.5 text-[16px] font-semibold">{unitSuffix[kpi.key]}</span>
                )}
              </span>
              <ChangeBadge change={kpi.change} unit={kpi.unit} />
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
