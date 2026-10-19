# FastAPI 백엔드 1단계 계획 (공식 스킬 적용)

## Context
대시보드 데이터는 `src/lib/mock-data.ts`에 하드코딩되어 있고, 컴포넌트는 `src/lib/api.ts`만 호출해요.
`backend/`의 FastAPI가 `src/types/dashboard.ts`와 같은 JSON을 내려주게 하고, 프론트는 `api.ts`만 바꿔요.
요구는 세 가지예요.
- 공식 기준만 따라요.
- 확장 가능한 구조로 만들어요.
- 패키지는 uv로 관리해요.

**이미 된 것**
- `backend/` 생성 완료: `pyproject.toml`, `uv.lock`, `.python-version` 3.12, FastAPI 0.143.0
- 공식 스킬은 루트 `.claude/skills/fastapi/`에 두었고, fastapi-developer 에이전트가 미리 읽도록 연결했어요.

**근거 표기**
- [SKILL] FastAPI 공식 스킬
- [TPL] 공식 템플릿 0.12.0
- [TPL-0.5] 공식 템플릿 0.5.0
- [DOC] Bigger Applications 문서
- [근거 없음] 공식 근거가 없는 부분

스킬은 폴더 구조를 규정하지 않아요. 그래서 폴더 배치는 TPL과 DOC를 따르고, 스킬은 코드 규칙과 도구 선택에 적용해요.

## 1단계 구조
```
backend/
├── pyproject.toml     # [SKILL][TPL] [tool.fastapi] entrypoint="app.main:app", dev 그룹, ruff
├── uv.lock, .python-version, .env.example
├── app/
│   ├── main.py        # [TPL] FastAPI(), CORS, app.include_router(api_router)
│   ├── models.py      # [TPL] 응답 모델 (camelCase 공통 베이스 포함)
│   ├── crud.py        # [TPL 이름] 조회 함수. 1단계는 내부에 mock 데이터 [근거 없음: mock 위치]
│   ├── core/config.py # [TPL] Settings: API_V1_STR, PROJECT_NAME, ENVIRONMENT, FRONTEND_HOST
│   └── api/
│       ├── deps.py    # [TPL][SKILL] Annotated 의존성 별칭 (1단계는 비어 있음)
│       ├── main.py    # api_router = APIRouter(prefix=settings.API_V1_STR); utils·dashboard include
│       └── routes/
│           ├── utils.py      # [TPL] APIRouter(prefix="/utils", tags=["utils"]) GET /health-check/
│           └── dashboard.py  # [TPL][SKILL] APIRouter(prefix="/dashboard", tags=["dashboard"]) GET 8개
└── tests/
    ├── conftest.py    # [TPL] TestClient
    └── api/routes/test_utils.py, test_dashboard.py
```
- 모든 패키지에 `__init__.py`를 둬요. [DOC]
- `/api/v1`은 `api_router`의 `APIRouter(prefix=...)`에서 한 번만 붙여요.
  - 스킬은 "prefix는 `include_router()`가 아니라 라우터에 선언"하라고 해요.
  - 템플릿은 `include_router(..., prefix=)`를 써요.
  - 둘을 맞추려고 템플릿의 `api_router` 구조는 유지하고, prefix만 라우터 쪽으로 옮겼어요.
- 최종 경로: `/api/v1/dashboard/*`, `/api/v1/utils/health-check/`

## 확장 구조
- 라우트는 리소스마다 파일 하나예요. `routes/{orders,products,users,settings,login}.py`. [TPL][DOC]
- DB를 도입할 때 추가할 것: `core/db.py`(SQLModel 세션), `core/security.py`, `alembic/`, `initial_data.py`(mock을 시드로 옮김), `api/deps.py`의 `SessionDep`/`CurrentUserDep`. [TPL][SKILL: SQLModel]
- 쪼개는 시점: 테이블을 가진 두 번째 도메인이 생기면 `models.py`/`crud.py`를 `models/<엔티티>.py`, `crud/crud_<엔티티>.py` 패키지로 바꿔요. [TPL-0.5]
  - `__init__.py`에서 이름을 다시 내보내 기존 import를 유지해요.
  - 이 시점은 제가 정한 기준이에요. [근거 없음: 시점]

## 스킬 코드 규칙 (전부 [SKILL])
- 라우트와 의존성은 기본 `def`로 써요. 확실히 논블로킹일 때만 `async def`를 써요.
- 반환 타입(`-> list[Kpi]`)을 선언해요. `response_model`은 공개 스키마가 다를 때만 써요.
- `Annotated[..., Depends()]`를 쓰고 타입 별칭을 만들어요. 파라미터도 `Annotated[..., Query()]`로 선언해요.
- Ellipsis(`...`), `RootModel`, `ORJSONResponse`는 쓰지 않아요.
- 함수 하나에 HTTP 메서드 하나만 둬요.
- DB는 SQLModel, 외부 HTTP는 HTTPX를 써요.

## 모델 규칙
- camelCase: `models.py`의 공통 베이스에 `ConfigDict(alias_generator=to_camel, validate_by_name=True)`를 둬요.
  - pydantic 2.14.1에서 `to_camel`과 `validate_by_name`이 있는 걸 확인했어요.
  - 템플릿은 snake_case로 응답해요. camelCase는 프론트 계약에 맞추려는 선택이에요. [근거 없음: 템플릿 관례 아님]
- 이름과 타입
  - TS의 `Order`는 `RecentOrder`로 이름을 바꿔요.
  - 값이 정해진 필드는 `Literal`로 써요.
  - `HourlyTraffic.values`는 `list[tuple[int,int,int]]`예요.
  - `TodoItem.urgent`는 `bool = False`예요.
- hourlyValue를 옮길 때는 `math.floor(x + 0.5)`를 써요. JS `Math.round`와 반올림 결과를 맞추기 위해서예요. 168개 값을 테스트로 대조해요.
- `getNavBadges`는 백엔드에 만들지 않아요. 프론트에서 `getTodos()` 결과로 계산해요.

## 엔드포인트 (`/api/v1/dashboard/*`, GET)
kpis, revenue-trend, category-shares, traffic-sources, hourly-traffic, recent-orders, todos, today-revenue
각각 `api.ts`의 `getKpis` … `getTodayRevenue`와 1:1로 대응해요.

## 툴링
```bash
cd backend
uv add pydantic-settings
uv add --dev ruff ty pytest      # httpx는 fastapi[standard]에 포함 (0.28.1 확인)
uv run fastapi dev               # :8000
uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run ty check
```
- ruff는 `select`에 `"FAST"`(FastAPI 규칙, 확인함)를 추가하고, 나머지는 템플릿 규칙을 기준으로 해요.
- 타입 검사는 mypy 대신 ty를 써요. [SKILL]

## 프론트 (`src/lib/api.ts`만)
- `request<T>(path, fallback)`를 만들어요.
  - `API_URL`이 없으면 mock을 반환해요.
  - 있으면 `${API_URL}/api/v1${path}`로 fetch하고, `!res.ok`면 throw해요.
- `getNavBadges`는 `getTodos()`를 쓰게 바꿔요.
- `.env.local`에는 `API_URL=http://localhost:8000`을 넣어요.
- 구현 전에 `node_modules/next/dist/docs/01-app/03-api-reference/04-functions/fetch.md`와 `01-getting-started/08-caching.md`를 읽고 캐시 옵션을 정해요.

## 구현 순서와 검증
1. 의존성 추가 → `core/config.py`, `main.py`, `api/main.py`, `routes/utils.py`
2. `models.py`, `crud.py`, `routes/dashboard.py`, 테스트 작성
3. pytest, ruff, ty가 통과하는지 확인해요.
4. `/docs`와 curl로 확인해요.
   - 키가 camelCase인지
   - hourly-traffic이 168개인지
   - health-check가 응답하는지
5. `api.ts`를 바꾸고 `/admin`이 기존 화면과 같은지 확인해요(KPI 5.9%, 히트맵, 배지).
6. `crud.py`의 값을 바꾸면 화면에 반영되는지 확인해요. API_URL이 없으면 mock, 백엔드를 끄면 에러가 나는지 확인해요.
7. `npx tsc --noEmit`, `npm run lint`, `npm run build`가 통과하는지 확인해요.
8. CLAUDE.md를 갱신해요.
   - 백엔드 명령어와 구조
   - "`dashboard.ts`와 `models.py`는 함께 수정" 규칙
   - 스킬 위치 메모
