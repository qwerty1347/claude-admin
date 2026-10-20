# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

## 프로젝트

한국어 관리자(Admin) 대시보드. Next.js 16 (App Router, Turbopack) + React 19 + TypeScript + Tailwind CSS v4 + ECharts 6.
백엔드는 `backend/` 의 FastAPI (Python 3.12, uv). 아직 DB 없이 mock 데이터를 API로 내려준다. 상세 계획은 `docs/BACKEND-PLAN.md`.

## 명령어

```bash
npm run dev      # 개발 서버 → http://localhost:3001 (/ 는 /admin 으로 리다이렉트)
npm run build    # 프로덕션 빌드 (타입 검사 포함)
npm run lint     # ESLint
npx tsc --noEmit # 타입 검사만
```

```bash
cd backend
uv run fastapi dev --port 8010   # 백엔드 → http://127.0.0.1:8010/docs (8000은 이 PC에서 다른 프로세스가 사용 중)
uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run ty check
```

- 프론트는 `.env.local` 의 `API_URL` 이 있으면 백엔드를 부르고, 없으면 mock 데이터를 쓴다 (예시: `.env.example`).
  `localhost` 가 아니라 `127.0.0.1` 로 적는다 (Node fetch 가 `::1` 로 풀면 연결 안 됨).
- 프론트 테스트 프레임워크는 아직 없다. 백엔드는 pytest.
- 이 폴더는 XAMPP `htdocs` 아래지만 Apache 주소(`localhost/www/...`)로는 동작하지 않는다. 반드시 `:3001`.
- Node 20.15 환경이라 일부 ESLint 의존성이 엔진 경고를 내지만 lint는 통과한다.

## 아키텍처

### 데이터 흐름 (가장 중요한 규칙)

```
backend (FastAPI /api/v1/dashboard/*)  ┐
lib/mock-data.ts (API_URL 없을 때)      ┴→  lib/api.ts (request<T>)  →  app/admin/page.tsx (서버 컴포넌트, Promise.all)
                                                   →  props  →  클라이언트 컴포넌트 (차트, 토글, 필터)
```

- 컴포넌트는 **`src/lib/api.ts` 의 함수만** 호출한다. mock-data나 fetch를 직접 쓰지 않는다.
- 백엔드 응답은 공통 틀로 감싸져 온다: 성공 `{statusCode, code, data}`, 실패 `{statusCode, code, message, errors}`.
  `request<T>()` 가 `.data` 만 꺼내 반환하고, 실패는 `ApiRequestError` 로 던진다 → `app/admin/error.tsx`, `app/error.tsx`.
- `request<T>()` 는 `cache: "no-store"` + 5초 타임아웃. `catch` 에서 `unstable_rethrow` 를 먼저 부른다 (빼면 `next build` 실패).
- 응답 형태는 `src/types/dashboard.ts` 에 정의. **`backend/app/schemas/dashboard.py` 와 함께 수정한다** (JSON 키는 camelCase).
- 서로 연결된 숫자는 **원천 데이터에서 계산**한다. 예: 매출 증감률·차액은 `RevenueTrend` 배열에서 계산하고,
  `kpis[].change` 같은 별도 하드코딩 값과 섞지 않는다 (이전에 12.4% vs 실제 5.9% 불일치 버그가 있었음).
  사이드바 배지(`getNavBadges`)도 `todos`에서 계산한다.

### 라우팅 / 레이아웃

- `app/layout.tsx`: 루트. Pretendard 가변 폰트(`next/font/local`, `node_modules/pretendard`)만 로드.
- `app/admin/layout.tsx` (서버) → `components/layout/AdminShell.tsx` (클라이언트) 가 Sidebar + Header 를 감싼다.
  사이드바는 관리자 영역에만 있으므로 `/login` 같은 페이지는 `app/admin` 밖에 만들면 된다.
- 관리자 메뉴 추가: `app/admin/<이름>/page.tsx` 생성 + `components/layout/nav-items.ts` 에 한 줄 추가.
  아직 구현 안 된 메뉴는 `components/common/ComingSoon.tsx` 를 렌더한다.
- 사이드바 데스크톱 접힘 상태는 `use-sidebar-collapsed.ts` (`useSyncExternalStore` + localStorage, 실패 시 메모리)로 관리.

### 차트 (ECharts)

- 모든 차트는 `components/charts/EChart.tsx` 래퍼를 통한다. ECharts는 `echarts/core` 에서 **필요한 것만 등록**하므로,
  새 차트 타입/컴포넌트를 쓰면 `EChart.tsx` 의 `echarts.use([...])` 에 추가해야 한다 (안 하면 빈 화면).
- 래퍼가 `useEffect` 에서 init, `ResizeObserver` 로 리사이즈, 페이지 폰트를 `textStyle.fontFamily` 로 주입한다.
- ECharts 6: `grid.containLabel` 은 폐기됨 → `outerBoundsMode: "same", outerBoundsContain: "axisLabel"` 사용.
- 차트 색/공통 스타일은 `components/charts/theme.ts` (globals.css 토큰과 같은 값을 유지).
- 차트 컴포넌트는 `option` 을 `useMemo` 로 만든다 (매 렌더 setOption 방지).

### 디자인 시스템

- 색상 토큰은 `src/app/globals.css` 의 `@theme` 에 정의 → Tailwind 클래스로 사용
  (`bg-canvas`, `bg-surface`, `text-ink`, `text-sub`, `text-muted`, `border-line`, `bg-primary`, `rounded-card` 등).
- **증가 = 빨강(`text-rise`), 감소 = 파랑(`text-fall`)** — 국내 증권 앱 관례.
- 카드 패턴: 테두리·그림자 없이 흰 배경 + `rounded-card`, 작은 제목(`text-sub`) 아래 결론 한 문장(큰 글씨).
- 금액·숫자 포맷은 `src/lib/format.ts` 사용: `formatWonKorean`(1억 2,845만원), `formatWonShort`(축 라벨),
  `formatNumber`, `formatPercent`, 조사 자동 선택 `withSubjectParticle`("의류가"/"식품이").
- UI 문구는 한국어 해요체 문장으로, 숫자만 던지지 말고 의미를 말한다 (예: "지난달보다 5.9% 늘었어요", "토요일 11시에 가장 붐벼요").
- 공통 인터랙션 컴포넌트: `components/common/Segmented.tsx` (보기/기간 전환),
  `components/common/RollingTicker.tsx` (한 줄에서 위로 굴러가며 바뀌는 띠. 호버 시 정지, reduced-motion 대응,
  스크린리더용 목록 별도 제공).

## 작업 시 주의

- **한글이 들어간 파일을 PowerShell(`Get-Content`/`Set-Content`)로 수정하지 말 것** — Windows PowerShell 5.1이 UTF-8을
  CP949로 읽어 한글이 깨진다. Edit/Write 도구나 Bash를 쓴다.
- Playwright MCP는 스크린샷·콘솔 로그를 프로젝트 안 `.playwright-mcp/`(gitignore됨)에 쓴다. 이 쓰기가 Next 파일 감시를
  건드려, **Playwright로 페이지를 열어 둔 채 소스를 수정하면 Fast Refresh가 무한 반복**된다.
  소스 수정 전 `browser_close`, 확인할 때만 다시 연다. ECharts는 그려지기까지 시간이 걸리므로 스크린샷 전 1~2초 대기.
- 개발 서버가 이미 3001 포트에서 떠 있으면 두 번째 `next dev` 는 바로 종료된다 (기존 서버를 쓰면 됨).
- `docs/PLAN.md` 에 초기 설계 플랜, `docs/BACKEND-PLAN.md` 에 백엔드 계획·규칙이 있다.
- FastAPI 공식 스킬은 `.claude/skills/fastapi/` 에 있다. 백엔드 코드는 이 스킬 규칙(Annotated, 반환 타입, 기본 `def`)을 따른다.
