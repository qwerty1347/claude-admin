"use client";

import { useMemo } from "react";
import EChart from "./EChart";
import { axisLabel, colors, tooltipBase } from "./theme";
import { formatNumber } from "@/lib/format";
import type { TrafficSource } from "@/types/dashboard";

export default function TrafficBarChart({ data, className = "h-80" }: { data: TrafficSource[]; className?: string }) {
  const option = useMemo(() => {
    // 가로 막대는 아래→위로 그려지므로 큰 값이 위에 오도록 뒤집는다.
    const sorted = [...data].sort((a, b) => a.visitors - b.visitors);
    const top = sorted.length - 1;
    return {
      tooltip: {
        ...tooltipBase,
        trigger: "axis",
        axisPointer: { type: "none" },
        valueFormatter: (v: number) => `${formatNumber(v)}명`,
      },
      grid: { left: 4, right: 64, top: 4, bottom: 4, outerBoundsMode: "same", outerBoundsContain: "axisLabel" },
      xAxis: { type: "value", show: false },
      yAxis: {
        type: "category",
        data: sorted.map((d) => d.channel),
        axisLabel: { ...axisLabel, color: colors.sub, fontSize: 13, margin: 12 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [
        {
          name: "방문자",
          type: "bar",
          barWidth: 14,
          showBackground: true,
          backgroundStyle: { color: colors.canvas, borderRadius: 7 },
          // 1위 채널만 진하게
          data: sorted.map((d, i) => ({
            value: d.visitors,
            itemStyle: { color: i === top ? colors.primary : "#90c2ff", borderRadius: 7 },
          })),
          label: {
            show: true,
            position: "right",
            distance: 10,
            color: colors.ink,
            fontSize: 13,
            fontWeight: 600,
            formatter: (p: { value: number }) => `${formatNumber(p.value)}명`,
          },
        },
      ],
    };
  }, [data]);

  return <EChart option={option} className={className} />;
}
