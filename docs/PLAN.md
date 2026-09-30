# 관리자 페이지 (Next.js 16 + ECharts) 플랜

## Context
처음에는 `/`에 대시보드 1페이지만 두려고 했으나, **관리자 영역(`/admin`)을 만들고 그 첫 화면(index)을 대시보드로** 하는 구조로 변경한다. 이렇게 하면 나중에 회원·주문 관리 같은 메뉴나 로그인 페이지를 추가하기 쉽다.
데이터는 하드코딩하되, 데이터 접근을 `lib/api.ts` 한 곳으로 모아 나중에 백엔드 API로 교체할 때 컴포넌트를 건드리지 않게 한다.

## 현재 상태 (완료)
- Next.js 16.3.7 + React 19 + TypeScript + Tailwind v4 + ESLint, `src/app` 구조로 생성
- git 초기화 및 첫 커밋 `ba85eb2` (create-next-app 자동)
- `CLAUDE.md`(`@AGENTS.md` 참조), `AGENTS.md` 자동 생성
- `docs/PLAN.md` (이전 플랜 사본, 미커밋) → 이 플랜으로 교체 예정
- 주의: Node 20.15.1 → ESLint 일부 패키지가 20.19+ 요구 (lint 실패 시 Node 22 LTS 권장)

## URL 구조
| URL | 화면 |
|---|---|
| `/` | `/admin`으로 리다이렉트 |
| `/admin` | **대시보드** (index) |
| `/admin/users` | 회원 관리 (빈 페이지: "준비 중") |
| `/admin/orders` | 주문 관리 (빈 페이지) |
| `/admin/products` | 상품 관리 (빈 페이지) |
| `/admin/settings` | 설정 (빈 페이지) |

## 파일 구조
```
src/
  app/
    layout.tsx                  # 루트: <html lang="ko">, 폰트, globals.css만 (사이드바 X)
    page.tsx                    # redirect('/admin')  (next/navigation)
    globals.css
    admin/
      layout.tsx                # 관리자 공통 틀: Sidebar + Header + {children}
      page.tsx                  # 대시보드 (서버 컴포넌트, lib/api에서 데이터 조회)
      loading.tsx               # 로딩 스켈레톤
      users/page.tsx            # 빈 페이지 (공통 ComingSoon 컴포넌트 사용)
      orders/page.tsx
      products/page.tsx
      settings/page.tsx
  components/
    layout/Sidebar.tsx          # 'use client' — usePathname으로 활성 메뉴 표시, 모바일 토글
    layout/Header.tsx           # 현재 페이지 제목, 검색창, 프로필
    layout/nav-items.ts         # 메뉴 목록 한 곳에서 관리 (label, href, icon)
    common/ComingSoon.tsx       # "준비 중" 빈 페이지 표시
    dashboard/KpiCard.tsx       # 값 + 전기 대비 증감률(▲▼)
    dashboard/RecentOrdersTable.tsx
    charts/EChart.tsx           # 'use client' echarts-for-react 래퍼 (SSR 끔, 리사이즈 대응)
    charts/RevenueTrendChart.tsx   # 월별 매출/주문 (라인+바, 이중 Y축)
    charts/CategoryPieChart.tsx    # 카테고리별 매출 비중 (도넛)
    charts/TrafficBarChart.tsx     # 유입 채널별 방문자 (가로 막대)
    charts/HourlyHeatmapChart.tsx  # 요일×시간대 접속 히트맵
  lib/
    mock-data.ts                # 하드코딩 데이터
    api.ts                      # getKpis(), getRevenueTrend() … async 함수 (지금 mock, 나중에 fetch)
    format.ts                   # 금액/숫자 포맷 (Intl.NumberFormat('ko-KR'))
  types/dashboard.ts            # 데이터 타입 (= 나중 API 응답 스키마)
```
→ 새 관리자 메뉴 추가 = `app/admin/<이름>/page.tsx` 생성 + `nav-items.ts`에 한 줄 추가.

## 대시보드 구성 (`/admin`)
1. KPI 카드 4개: 총 매출, 주문 수, 신규 가입자, 전환율
2. 매출 추이 콤보 차트(2/3) + 카테고리 도넛(1/3)
3. 유입 채널 막대 + 시간대 히트맵
4. 최근 주문 테이블 (주문번호, 고객, 금액, 상태 배지, 일시)
- 반응형: 모바일 1열 → md 2열 → xl 그리드, 모바일에서 사이드바 토글
- UI 텍스트 한국어, 차트 색상은 공통 팔레트 상수로 통일

## 핵심 설계 포인트
- **레이아웃 분리**: 사이드바는 `app/admin/layout.tsx`에만 → 나중에 `/login` 등은 사이드바 없이 만들 수 있음. 메뉴 이동 시 레이아웃 유지.
- **서버/클라이언트 경계**: `admin/page.tsx`(서버)가 `lib/api.ts`로 데이터를 받아 차트(클라이언트)에 props로 전달. ECharts는 `'use client'` 컴포넌트 안에서만 사용, `next/dynamic`(ssr:false)로 hydration 에러 방지.
- **데이터 경계**: 컴포넌트는 `lib/api.ts`만 호출. 백엔드 연동 시 `api.ts` 내부만 `fetch(process.env.NEXT_PUBLIC_API_URL + …)`로 교체.
- 코드 작성 전 `node_modules/next/dist/docs/`의 해당 가이드 확인 (AGENTS.md 지시, Next 16 변경점).

## 작업 순서
1. `npm i echarts echarts-for-react lucide-react`
2. 루트 `layout.tsx` 정리, `page.tsx` → redirect
3. `admin/layout.tsx` + Sidebar/Header/nav-items → 브라우저 확인, 커밋
4. `types` → `mock-data` → `api.ts`
5. KPI 카드 + 차트 1개(매출 추이) → 확인, 커밋
6. 나머지 차트 3개 + 최근 주문 테이블 + loading → 확인, 커밋
7. 빈 메뉴 페이지 4개 (ComingSoon)
8. `CLAUDE.md`에 프로젝트 규칙 추가, `.claude/settings.json`(npm 명령 허용), `docs/PLAN.md`를 이 플랜으로 갱신 → 커밋

## 로컬 실행
- `npm run dev` → http://localhost:3000 (자동으로 /admin 이동)
- XAMPP Apache 주소(`localhost/www/...`)로는 동작하지 않음. 반드시 `:3000`.

## 검증
1. `/` 접속 → `/admin`으로 이동
2. `/admin`: KPI 4개, 차트 4개 렌더링, 툴팁 동작, 창 크기 변경 시 차트 리사이즈, 콘솔에 hydration 경고 없음
3. 사이드바 메뉴 클릭 → 각 페이지 이동, 활성 메뉴 강조, 사이드바는 새로 그려지지 않음
4. 모바일 폭(375px)에서 레이아웃 1열 + 사이드바 토글
5. `npm run build` 성공, `npm run lint` (Node 버전 문제 시 결과 보고)
