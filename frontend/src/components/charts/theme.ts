// 모든 차트가 공유하는 색상과 공통 스타일 (globals.css 의 토큰과 같은 값)
export const colors = {
  primary: "#3182f6",
  primaryStrong: "#1b64da",
  primarySoft: "#c9e2ff",
  ink: "#191f28",
  sub: "#4e5968",
  muted: "#8b95a1",
  line: "#e5e8eb",
  canvas: "#f2f4f6",
};

// 범주형(카테고리) 색상: 서로 구분이 잘 되는 순서로
export const palette = ["#3182f6", "#03b26c", "#fe9800", "#f04452", "#a234c7", "#b0b8c1"];

export const axisLabel = { color: colors.muted, fontSize: 12 };

export const splitLine = { lineStyle: { color: colors.line, type: "dashed" as const } };

export const tooltipBase = {
  backgroundColor: "#ffffff",
  borderWidth: 0,
  padding: [10, 14],
  extraCssText: "border-radius:12px;box-shadow:0 4px 20px rgba(25,31,40,0.12);",
  textStyle: { color: colors.ink, fontSize: 13 },
};
