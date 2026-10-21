"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { BarChart, HeatmapChart, LineChart, PieChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
  VisualMapComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsCoreOption } from "echarts/core";

// 사용하는 차트/컴포넌트만 등록해 번들 크기를 줄인다. 새 차트 종류를 쓰면 여기에 추가.
echarts.use([
  BarChart,
  HeatmapChart,
  LineChart,
  PieChart,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  VisualMapComponent,
  CanvasRenderer,
]);

type Props = {
  option: EChartsCoreOption;
  className?: string;
};

// ECharts는 브라우저 DOM이 필요하므로 useEffect 안에서만 초기화한다 (서버 렌더링 시엔 빈 div).
export default function EChart({ option, className = "h-80" }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = echarts.init(container);
    chartRef.current = chart;

    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    // 캔버스는 CSS 폰트를 상속하지 않으므로 페이지 폰트(Pretendard)를 직접 지정한다.
    const fontFamily = containerRef.current
      ? getComputedStyle(containerRef.current).fontFamily
      : undefined;
    chartRef.current?.setOption({ textStyle: { fontFamily }, ...option }, true);
  }, [option]);

  return <div ref={containerRef} className={`w-full ${className}`} />;
}
