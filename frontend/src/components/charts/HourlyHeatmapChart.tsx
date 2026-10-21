"use client";

import { useMemo } from "react";
import EChart from "./EChart";
import { axisLabel, colors, tooltipBase } from "./theme";
import { formatNumber } from "@/lib/format";
import type { HourlyTraffic } from "@/types/dashboard";

export default function HourlyHeatmapChart({ data, className = "h-80" }: { data: HourlyTraffic; className?: string }) {
  const option = useMemo(() => {
    const max = Math.max(...data.values.map(([, , v]) => v));
    return {
      tooltip: {
        ...tooltipBase,
        position: "top",
        formatter: (p: { value: [number, number, number] }) => {
          const [h, d, v] = p.value;
          return `${data.days[d]}요일 ${data.hours[h]}<br/><b>평균 ${formatNumber(v)}명</b>`;
        },
      },
      grid: { left: 4, right: 4, top: 4, bottom: 44, outerBoundsMode: "same", outerBoundsContain: "axisLabel" },
      xAxis: {
        type: "category",
        data: data.hours,
        axisLabel: { ...axisLabel, interval: 2 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: "category",
        data: data.days,
        inverse: true,
        axisLabel: { ...axisLabel, color: colors.sub, fontSize: 13 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      visualMap: {
        min: 0,
        max,
        calculable: false,
        orient: "horizontal",
        right: 0,
        bottom: 0,
        itemWidth: 10,
        itemHeight: 120,
        text: ["많음", "적음"],
        textGap: 8,
        textStyle: axisLabel,
        inRange: { color: [colors.canvas, "#c9e2ff", "#64a8ff", colors.primary, colors.primaryStrong] },
      },
      series: [
        {
          name: "접속자",
          type: "heatmap",
          data: data.values,
          itemStyle: { borderColor: "#fff", borderWidth: 2, borderRadius: 4 },
          emphasis: { itemStyle: { borderColor: colors.ink, borderWidth: 1 } },
        },
      ],
    };
  }, [data]);

  return <EChart option={option} className={className} />;
}
