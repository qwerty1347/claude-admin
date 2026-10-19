"use client";

import { useMemo } from "react";
import EChart from "./EChart";
import { palette, tooltipBase } from "./theme";
import { formatWonKorean } from "@/lib/format";
import type { CategoryShare } from "@/types/dashboard";

export default function CategoryPieChart({ data }: { data: CategoryShare[] }) {
  const total = data.reduce((sum, d) => sum + d.value, 0);

  const option = useMemo(
    () => ({
      color: palette,
      tooltip: {
        ...tooltipBase,
        trigger: "item",
        formatter: (p: { marker: string; name: string; value: number; percent: number }) =>
          `${p.marker}${p.name}&nbsp;&nbsp;<b>${formatWonKorean(p.value)}</b> (${p.percent}%)`,
      },
      series: [
        {
          name: "카테고리",
          type: "pie",
          radius: ["66%", "92%"],
          padAngle: 1.5,
          itemStyle: { borderRadius: 4 },
          label: { show: false },
          emphasis: { scale: true, scaleSize: 4 },
          data,
        },
      ],
    }),
    [data],
  );

  return (
    <div>
      <div className="relative">
        <EChart option={option} className="h-48" />
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[13px] text-muted">합계</span>
          <span className="text-[17px] font-bold text-ink">{formatWonKorean(total)}</span>
        </div>
      </div>

      <ul className="mt-5 space-y-2.5">
        {data.map((item, i) => (
          <li key={item.name} className="flex items-center gap-2.5 text-[14px]">
            <span
              className="size-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: palette[i % palette.length] }}
              aria-hidden
            />
            <span className="text-sub">{item.name}</span>
            <span className="ml-auto font-semibold text-ink">
              {((item.value / total) * 100).toFixed(1)}%
            </span>
            <span className="w-24 text-right text-muted">{formatWonKorean(item.value)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
