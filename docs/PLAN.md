# 관리자 대시보드 (Next.js + ECharts) 플랜

## Context
빈 디렉터리(`C:\xampp\htdocs\www\projects\claude-dashboard`)에 관리자 대시보드를 새로 만든다. 프론트엔드는 Next.js, 차트는 ECharts. 백엔드는 나중에 붙일 수 있으므로 지금은 하드코딩 데이터를 쓰되, **데이터 접근을 한 곳(service 레이어)으로 모아서** 나중에 API 호출로 바꿀 때 컴포넌트를 건드리지 않게 한다. Node 20.15.1 / npm 10.7 확인됨.

## 스택
- Next.js (App Router, TypeScript, `src/` 디렉터리) — `create-next-app` 최신
- Tailwind CSS (create-next-app 기본 포함)
- `echarts` + `echarts-for-react`
- 아이콘: `lucide-react`

## 스캐폴딩
```
npx create-next-app@latest . --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-turbopack(필요 시)
npm i echarts echarts-for-react lucide-react
```

## 구조
```
src/
  app/
    layout.tsx            # 사이드바 + 헤더 공통 레이아웃
    page.tsx              # 메인 대시보드 (서버 컴포넌트, 데이터 로드)
    globals.css
  components/
    layout/Sidebar.tsx    # 메뉴(대시보드 활성, 나머지는 자리만)
    layout/Header.tsx     # 페이지 제목, 검색창, 프로필
    dashboard/KpiCard.tsx # 값 + 전기 대비 증감률
    dashboard/RecentOrdersTable.tsx
    charts/EChart.tsx     # 'use client', echarts-for-react 래퍼 (dynamic import ssr:false, resize 대응)
    charts/RevenueTrendChart.tsx   # 월별 매출/주문 (라인+바 콤보, 이중 Y축)
    charts/CategoryPieChart.tsx    # 카테고리별 매출 비중 (도넛)
    charts/TrafficBarChart.tsx     # 유입 채널별 방문자 (가로 막대)
    charts/HourlyHeatmapChart.tsx  # 요일×시간대 접속 히트맵
  lib/
    mock-data.ts          # 하드코딩 데이터
    api.ts                # getKpis(), getRevenueTrend(), ... async 함수 — 지금은 mock 반환, 나중에 fetch로 교체
  types/dashboard.ts      # 데이터 타입 정의 (API 응답 스키마 역할)
```

## 페이지 구성 (page.tsx)
1. KPI 카드 4개: 총 매출, 주문 수, 신규 가입자, 전환율 (증감률 ▲▼ 색상 표시)
2. 1행: 매출 추이 콤보 차트(2/3 폭) + 카테고리 도넛(1/3 폭)
3. 2행: 유입 채널 막대 + 시간대 히트맵
4. 최근 주문 테이블 (주문번호, 고객, 금액, 상태 배지, 일시)
- 반응형: 모바일 1열 → md 2열 → xl 그리드. 사이드바는 모바일에서 토글.

## 핵심 설계 포인트
- **데이터 경계**: 컴포넌트는 `lib/api.ts` 함수만 호출. 백엔드 연동 시 `api.ts` 내부만 `fetch(process.env.NEXT_PUBLIC_API_URL + ...)`로 교체.
- **ECharts SSR 이슈**: 차트 컴포넌트는 `'use client'`, `EChart` 래퍼에서 `next/dynamic`(ssr:false)로 로드해 hydration 에러 방지. 서버 컴포넌트(page)에서 데이터를 받아 props로 전달.
- 차트 색상은 공통 팔레트 상수 하나로 통일, 툴팁/범례 한글화, 금액은 `Intl.NumberFormat('ko-KR')` 포맷.
- UI 텍스트는 한국어.

## 검증
1. `npm run build` — 타입/빌드 에러 없음
2. `npm run dev` → http://localhost:3000 접속, 4개 차트 렌더링·툴팁·창 크기 변경 시 리사이즈 확인, 콘솔 hydration 경고 없음
3. `npm run lint`
