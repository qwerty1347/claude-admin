"use client";

import { useMemo } from "react";
import EChart from "./EChart";
import { axisLabel, colors, splitLine, tooltipBase } from "./theme";
import { formatNumber, formatWonKorean, formatWonShort } from "@/lib/format";
import type { RevenueTrend } from "@/types/dashboard";

export default function RevenueTrendChart({ data }: { data: RevenueTrend }) {
  const option = useMemo(() => {
    const last = data.revenue.length - 1;
    return {
      tooltip: {
        ...tooltipBase,
        trigger: "axis",
        axisPointer: { type: "shadow", shadowStyle: { color: "rgba(49,130,246,0.06)" } },
        formatter: (params: { seriesName: string; value: number; marker: string; axisValue: string }[]) =>
          [
            `<b>${params[0]?.axisValue}</b>`,
            ...params.map((p) =>
              `${p.marker}${p.seriesName}&nbsp;&nbsp;<b>${
                p.seriesName === "매출" ? formatWonKorean(p.value) : `${formatNumber(p.value)}건`
              }</b>`,
            ),
          ].join("<br/>"),
      },
      legend: {
        top: 0,
        right: 0,
        itemGap: 16,
        itemWidth: 10,
        itemHeight: 10,
        textStyle: { color: colors.sub, fontSize: 13 },
        data: [
          { name: "매출", icon: "roundRect", itemStyle: { color: colors.primary } },
          { name: "주문", icon: "circle", itemStyle: { color: colors.sub } },
        ],
      },
      grid: { left: 4, right: 4, top: 44, bottom: 4, outerBoundsMode: "same", outerBoundsContain: "axisLabel" },
      xAxis: {
        type: "category",
        data: data.months,
        axisLabel: { ...axisLabel, margin: 12 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: [
        {
          type: "value",
          axisLabel: { ...axisLabel, formatter: formatWonShort },
          splitLine,
        },
        {
          type: "value",
          axisLabel: { ...axisLabel, formatter: (v: number) => `${formatNumber(v)}건` },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "매출",
          type: "bar",
          barMaxWidth: 32,
          // 이번 달만 진하게, 지난 달들은 옅게
          data: data.revenue.map((value, i) => ({
            value,
            itemStyle: {
              color: i === last ? colors.primary : colors.primarySoft,
              borderRadius: [8, 8, 0, 0],
            },
          })),
          emphasis: { itemStyle: { color: colors.primary } },
        },
        {
          name: "주문",
          type: "line",
          yAxisIndex: 1,
          data: data.orders,
          smooth: 0.3,
          symbol: "circle",
          symbolSize: 6,
          showSymbol: false,
          itemStyle: { color: colors.sub },
          lineStyle: { width: 2, color: colors.sub },
        },
      ],
    };
  }, [data]);

  return <EChart option={option} className="h-72" />;
}
