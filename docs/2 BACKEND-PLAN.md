# FastAPI 백엔드 1단계 계획 (공식 스킬 적용)

## Context
대시보드 데이터는 `frontend/src/lib/mock-data.ts`에 하드코딩되어 있고, 컴포넌트는 `frontend/src/lib/api.ts`만 호출해요.
`backend/`의 FastAPI가 `frontend/src/types/dashboard.ts`와 같은 JSON을 내려주게 하고, 프론트는 `api.ts`만 바꿔요.
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
│   ├── schemas/       # API 요청·응답 스키마 (Pydantic). 도메인별 파일 [TPL-0.5: schemas/ 분리]
│   │   ├── __init__.py   # 다시 내보내기 → from app.schemas import Kpi
│   │   ├── common.py     # CamelModel, ApiResponse[T], ApiError, FieldError
│   │   └── dashboard.py  # Kpi ~ TodayRevenue (dashboard.ts 와 1:1)
│   ├── crud/          # 조회·저장 함수. 도메인별 파일 (schemas/ 와 같은 이름) [TPL-0.5: crud/ 분리]
│   │   └── dashboard.py  # 대시보드 조회 8개. 1단계는 내부에 mock 데이터 [근거 없음: mock 위치]
│   ├── utils.py       # [TPL] 범용 헬퍼: round_half_up, percent_change
│   ├── core/config.py # [TPL] Settings: API_PREFIX, PROJECT_NAME, ENVIRONMENT, FRONTEND_HOST, TIMEZONE
│   ├── core/clock.py  # utcnow()/now()/start_of_today() [근거 없음: 모듈 분리는 제 선택]
│   └── api/
│       ├── deps.py    # [TPL][SKILL] Annotated 의존성 별칭 (1단계는 비어 있음)
│       ├── main.py    # api_router = APIRouter(prefix=settings.API_PREFIX); v1.router include
│       └── v1/
│           ├── __init__.py   # router = APIRouter(prefix="/v1"); utils·dashboard include
│           └── routes/
│               ├── utils.py      # [TPL] APIRouter(prefix="/utils", tags=["utils"]) GET /health-check/
│               └── dashboard.py  # [TPL][SKILL] APIRouter(prefix="/dashboard", tags=["dashboard"]) GET 8개
└── tests/
    ├── conftest.py    # [TPL] TestClient
    ├── core/test_clock.py
    └── api/v1/routes/test_utils.py, test_dashboard.py
```
- 모든 패키지에 `__init__.py`를 둬요. [DOC]
- 경로 앞부분은 라우터마다 한 번씩만 붙여요. `api_router`(`/api`) → `v1.router`(`/v1`) → 리소스 라우터(`/dashboard`).
  - 스킬은 "prefix는 `include_router()`가 아니라 라우터에 선언"하라고 해요.
  - 템플릿은 `API_V1_STR`을 설정에 두고 `include_router(..., prefix=)`를 써요.
  - 버전은 환경마다 바뀌는 값이 아니라서 설정에서 빼고 `app/api/v1/` 패키지로 나눴어요. 설정에는 공통 `API_PREFIX="/api"`만 둬요. [근거 없음: 버전 패키지 분리는 제 선택]
  - v2가 생기면 `app/api/v2/`를 만들고 `api/main.py`에 `include_router(v2.router)` 한 줄을 추가해요. 바뀌지 않은 라우트는 v1 모듈을 재사용해요.
- 최종 경로: `/api/v1/dashboard/*`, `/api/v1/utils/health-check/`, OpenAPI는 `/api/openapi.json`

## 헬퍼 위치
- Python에는 전역 헬퍼가 없어서 모듈에 두고 import해서 써요.
- 범용 함수(두 곳 이상에서 사용) → `app/utils.py`. 많아지면 `app/utils/` 패키지(`text.py`, `money.py` …)로 나눠요.
- 한 기능에서만 쓰는 함수 → 그 기능 근처(`crud/<도메인>.py` 등). 앱 기반 기능(설정·시간·보안·DB) → `app/core/`.
- 화면 표시용 포맷은 프론트 `frontend/src/lib/format.ts` 담당이에요. 백엔드는 원래 값을 내려줘요.

## 확장 구조
- 라우트는 리소스마다 파일 하나예요. `api/v1/routes/{orders,products,users,settings,login}.py`. [TPL][DOC]
- DB를 도입할 때 추가할 것: `core/db.py`(엔진·세션, 비동기+동기), `core/security.py`, `alembic/`, `seeds/`(개발·데모용 시드, mock을 옮김), `api/deps.py`의 `AsyncSessionDep`/`SessionDep`/`CurrentUserDep`. [TPL] 자세한 건 아래 "DB 접근"
- 스키마(API 형태)는 `schemas/<도메인>.py`로 이미 나눴어요 (2026-10-19). DB 테이블 모델은 도입할 때 `models/<엔티티>.py`에 따로 둬요. DB 컬럼과 API로 내보내는 형태는 다를 수 있어서 구분해요. [TPL-0.5]
- 조회·저장 함수도 `crud/<도메인>.py`로 나눴어요 (2026-10-19). 라우트에서는 `from app.crud import dashboard as dashboard_crud`로 써요.
- 업무 규칙(상태 변경, 검증, 여러 테이블 처리)이 두꺼워지는 도메인만 `services/<도메인>.py`로 뽑아내요. 처음부터 계층을 나누지는 않아요.
  - `__init__.py`에서 이름을 다시 내보내 기존 import를 유지해요.
  - 이 시점은 제가 정한 기준이에요. [근거 없음: 시점]

## 스킬 코드 규칙 (전부 [SKILL])
- 라우트와 의존성은 기본 `def`로 써요. 확실히 논블로킹일 때만 `async def`를 써요.
- 반환 타입(`-> list[Kpi]`)을 선언해요. `response_model`은 공개 스키마가 다를 때만 써요.
- `Annotated[..., Depends()]`를 쓰고 타입 별칭을 만들어요. 파라미터도 `Annotated[..., Query()]`로 선언해요.
- Ellipsis(`...`), `RootModel`, `ORJSONResponse`는 쓰지 않아요.
- 함수 하나에 HTTP 메서드 하나만 둬요.
- 외부 HTTP는 HTTPX를 써요.
- 스킬은 DB로 SQLModel을 권장해요. 이 프로젝트는 SQLAlchemy 2를 직접 써요. 비동기와 동기를 둘 다 쓰는 구성이라 문서와 예제가 많은 쪽을 골랐어요(2026-10-20 결정). [선택: 스킬과 다름]

## 모델 규칙
- camelCase: `schemas/common.py`의 공통 베이스 `CamelModel`에 `ConfigDict(alias_generator=to_camel, validate_by_name=True)`를 둬요.
  - pydantic 2.14.1에서 `to_camel`과 `validate_by_name`이 있는 걸 확인했어요.
  - 템플릿은 snake_case로 응답해요. camelCase는 프론트 계약에 맞추려는 선택이에요. [근거 없음: 템플릿 관례 아님]
- 이름과 타입
  - TS의 `Order`는 `RecentOrder`로 이름을 바꿔요.
  - 값이 정해진 필드는 `Literal`로 써요.
  - `HourlyTraffic.values`는 `list[tuple[int,int,int]]`예요.
  - `TodoItem.urgent`는 `bool = False`예요.
- hourlyValue를 옮길 때는 `utils.round_half_up()`(`math.floor(x + 0.5)`)을 써요. JS `Math.round`와 반올림 결과를 맞추기 위해서예요. 168개 값을 테스트로 대조해요.
- `getNavBadges`는 백엔드에 만들지 않아요. 프론트에서 `getTodos()` 결과로 계산해요.

## 타임존 (Asia/Seoul)
- FastAPI·Python에는 전역 설정이 없어요. 그래서 설정값 하나와 시각 함수 하나로 관리해요.
- `core/config.py`: `TIMEZONE: str = "Asia/Seoul"`, `settings.tz`(ZoneInfo). `.env`로 덮어쓸 수 있어요.
- `core/clock.py`: 현재 시각은 여기서만 얻어요. `datetime.now()`를 직접 부르지 않아요.
  - `now()`: 업무 기준 시각이자 **DB 저장용** (서울, KST)
  - `start_of_today()`: 서울 기준 오늘 0시 (`today-revenue`의 "오늘" 경계)
  - `utcnow()`: 외부 연동(UTC를 요구하는 API, 토큰 만료 시각 등)에서만 써요. [TPL: `datetime.now(timezone.utc)`]
- **DB 저장은 KST예요** (2026-10-20 결정, `0 DOCKER-PLAN.md`의 MySQL `TZ: Asia/Seoul`).
  - DB 서버 시간대가 KST라서 `NOW()`와 `CURRENT_TIMESTAMP` 기본값도 KST예요. 앱도 `clock.now()`로 저장해서 기준을 하나로 맞춰요.
  - 컬럼은 `DATETIME`이에요. `TIMESTAMP`는 세션 시간대에 따라 값이 바뀌어 보이고 2038년 한계가 있어서 쓰지 않아요.
  - `DATETIME`에는 시간대 정보가 저장되지 않아요.
    - 저장할 때는 KST aware datetime에서 tzinfo를 떼서 넣어요.
    - 읽을 때는 `settings.tz`를 다시 붙여서 `AwareDatetime`(`+09:00`)으로 응답해요.
    - SQLAlchemy `TypeDecorator`를 하나 만들어 이 변환을 한 곳에서 해요.
  - 한국은 서머타임이 없어서 KST 저장으로 시간이 겹치거나 비는 문제가 없어요. 해외 사용자나 서버가 생기면 UTC 저장을 다시 검토해요.
- Windows는 OS 타임존 DB가 없어서 `tzdata` 패키지가 필수예요. 없으면 `ZoneInfoNotFoundError`가 나요.
- `RecentOrder.ordered_at`은 `AwareDatetime`으로 받고, JSON에는 `"2026-09-30T13:42:00+09:00"`로 내려가요.
  - 프론트 `RecentOrders.tsx`의 `orderedAt.split(" ")`가 깨지므로, `format.ts`에 `formatTime(iso)`
    (`Intl.DateTimeFormat`, `timeZone: "Asia/Seoul"`)를 추가하고 `mock-data.ts`의 `orderedAt`도 ISO로 바꿔요.

## DB 접근 (SQLAlchemy 2, 비동기 + 동기) — DB 도입 때 적용
MySQL 9.7 (`0 DOCKER-PLAN.md`). 같은 모델로 비동기 세션과 동기 세션을 둘 다 써요.

### 패키지
`uv add "sqlalchemy[asyncio]" aiomysql pymysql cryptography alembic`
- `aiomysql`: 비동기 드라이버. `pymysql`: 동기 드라이버. `cryptography`: MySQL 9 기본 인증(`caching_sha2_password`)에 필요해요.

### 접속 URL
- 설정에는 `DATABASE_URL` 하나만 둬요(비동기, `mysql+aiomysql://...?charset=utf8mb4`).
- 동기 URL은 드라이버 이름만 바꿔서 만들어요. 접속 정보가 두 군데로 갈라지지 않아요.
```python
# core/config.py
from sqlalchemy.engine import make_url

DATABASE_URL: str

@property
def database_url_sync(self) -> str:
    return make_url(self.DATABASE_URL).set(drivername="mysql+pymysql").render_as_string(hide_password=False)
```

### core/db.py
```python
class Base(DeclarativeBase): ...   # 모든 테이블 모델의 부모 (models/<엔티티>.py)

ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 3600}  # 끊긴 연결 감지, MySQL wait_timeout 전에 재연결

async_engine = create_async_engine(settings.DATABASE_URL, **ENGINE_OPTIONS)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.database_url_sync, **ENGINE_OPTIONS)
SessionLocal = sessionmaker(sync_engine, expire_on_commit=False)
```
- `expire_on_commit=False`: commit한 뒤 객체 속성을 읽을 때 다시 조회하지 않게 해요. 비동기에서는 이게 없으면 에러가 나요.
- lifespan 종료 시 `await async_engine.dispose()`, `sync_engine.dispose()`를 호출해요.
- KST `DATETIME` 변환용 `TypeDecorator`(위 타임존 섹션)도 여기에 둬요. 비동기와 동기 모두 같은 모델을 쓰니 한 번만 만들면 돼요.

### api/deps.py
```python
async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
SessionDep = Annotated[Session, Depends(get_session)]
```

### 어디서 무엇을 쓰나
| 위치 | 방식 | 이유 |
|---|---|---|
| API 라우트 (기본) | `async def` + `AsyncSessionDep` | DB 대기 중에 다른 요청을 처리해요. 스킬 규칙의 "확실히 논블로킹일 때만 async"에 해당해요 |
| 동기 라이브러리를 같이 쓰는 라우트 (엑셀 생성 등) | `def` + `SessionDep` | FastAPI가 스레드풀에서 실행해서 이벤트 루프를 막지 않아요 |
| Alembic 마이그레이션 | 동기 (`alembic init alembic`, `database_url_sync`) | 기본 템플릿 그대로라 단순해요 |
| 시드(`app/seeds/`), 관리 스크립트 | 동기 `SessionLocal()` | `asyncio.run` 없이 바로 실행해요 |
| 노트북 | 동기 `SessionLocal()` | Windows Jupyter의 이벤트 루프 문제를 피해요 (fastapi-tistory의 `run_async` 우회가 필요 없어요) |
| 테스트 데이터 준비 | 동기 `SessionLocal()` | API 호출은 TestClient로 하면 async 라우트도 그대로 테스트돼요 |

### 규칙
- **`async def` 안에서 동기 `Session`을 쓰지 않아요.** 이벤트 루프가 막혀서 그동안 모든 요청이 멈춰요. 반대로 `def` 안에서는 `AsyncSession`을 쓸 수 없어요.
- 한 요청 안에서 비동기 세션과 동기 세션을 섞지 않아요. 트랜잭션이 둘로 갈라져요.
- crud는 비동기를 기준으로 만들어요(`async def get_orders(session: AsyncSession)`). 동기 버전은 시드나 스크립트처럼 실제로 필요한 곳에만 만들어요. 모든 함수를 두 벌로 만들지 않아요.
- 비동기에서는 관계를 나중에 불러오는 lazy loading이 에러(`MissingGreenlet`)가 나요. `selectinload` / `joinedload`로 미리 불러와요.
- 엔진이 둘이라 커넥션 풀도 둘이에요. 기본 풀 크기(5 + overflow 10)씩이라 개발에서는 문제없어요. 운영에서는 MySQL `max_connections` 안에 들어오는지 확인해요.

## 엔드포인트 (`/api/v1/dashboard/*`, GET)
kpis, revenue-trend, category-shares, traffic-sources, hourly-traffic, recent-orders, todos, today-revenue
각각 `api.ts`의 `getKpis` … `getTodayRevenue`와 1:1로 대응해요.

## 응답 규격 (모든 API 공통) ✅ 2026-10-19 적용
성공·실패 판별은 **HTTP 상태 코드**로 해요. 본문의 `statusCode`는 같은 값을 한 번 더 적은 것(로그·디버깅용)이에요.
```jsonc
// 성공 2xx
{ "statusCode": 200, "code": "OK", "data": ... }
// 실패 4xx/5xx (HTTP 상태도 같은 값)
{ "statusCode": 422, "code": "VALIDATION_ERROR", "message": "입력값을 확인해 주세요",
  "errors": [{ "field": "query.page", "message": "..." }] }
```
- 성공은 모두 `code: "OK"`. 생성은 201. 본문 없는 204는 쓰지 않고 200 + `"data": null`.
- `code`는 프론트가 분기하는 기계용 값, `message`는 사람에게 보여주는 문구. `errors`는 항상 배열(없으면 `[]`).
- 500은 내부 내용을 본문에 넣지 않고 서버 로그에만 남겨요.
- 공통 code: `BAD_REQUEST`(400) `UNAUTHORIZED`(401) `FORBIDDEN`(403) `NOT_FOUND`(404) `METHOD_NOT_ALLOWED`(405)
  `CONFLICT`(409) `VALIDATION_ERROR`(422) `TOO_MANY_REQUESTS`(429) `INTERNAL_ERROR`(500).
  업무 에러는 `대상_상황` 대문자 스네이크 (`ORDER_ALREADY_SHIPPED`).
- 구현
  - 스키마: `schemas/common.py`의 `ApiResponse[T]`, `ApiError`, `FieldError`
  - 성공: 라우트에서 `return ApiResponse(data=...)`, 반환 타입 `-> ApiResponse[list[Kpi]]` (`/docs`에 data 타입 표시)
  - 실패: `raise AppError(409, "ORDER_ALREADY_SHIPPED", "이미 발송된 주문이에요")`.
    `core/errors.py`의 예외 핸들러 4개(AppError, 검증 실패, HTTPException, 예상 못 한 예외)가 모두 `ApiError`로 바꿔요.
  - 미들웨어로 자동 감싸지 않아요. 문서(`/docs`)와 실제 응답이 달라지기 때문이에요.
- 문서(/docs)와 실제 응답 맞추기 (2026-10-19 리뷰 반영)
  - 기본값이 있는 응답 필드(`statusCode`, `code`, `errors` 등)도 필수로 표시해요: `CamelModel`의 `json_schema_serialization_defaults_required=True`.
  - 실패 응답 문서는 실제로 낼 수 있는 상태만 붙여요. 공통(`api/main.py`)은 500만, 나머지는 라우트에서 `responses=error_responses(404, 422)`.
    파라미터가 있는 라우트는 FastAPI가 기본 형식 422를 자동으로 붙이므로 `error_responses(422)`로 덮어써요.
  - `HTTPException`은 문자열 detail이면 그대로 메시지로 써요. HTTP 기본 문구("Not Found" 등)와 문자열이 아닌 detail은 한글 기본 문구로 바꿔요.
    업무 에러는 code를 지정할 수 있는 `AppError`로 던지는 게 팀 규칙이에요.

## 툴링
```bash
cd backend
uv add pydantic-settings tzdata
uv add --dev ruff ty pytest      # httpx는 fastapi[standard]에 포함 (0.28.1 확인)
uv run fastapi dev --port 9101   # (도커는 루트에서 docker compose up -d, 0 DOCKER-PLAN.md)
uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run ty check
```
- ruff는 `select`에 `"FAST"`(FastAPI 규칙, 확인함)를 추가하고, 나머지는 템플릿 규칙을 기준으로 해요.
- 타입 검사는 mypy 대신 ty를 써요. [SKILL]

## 프론트 (`frontend/src/lib/api.ts`만)
- `request<T>(path, fallback)`를 만들어요.
  - `API_URL`이 없으면 mock을 반환해요.
  - 있으면 `${API_URL}/api/v1${path}`로 fetch해요.
  - `res.ok`면 응답 틀에서 `.data`만 꺼내 반환해요. 컴포넌트는 지금처럼 데이터만 받아요.
  - `!res.ok`면 본문(`ApiError`)의 `code`/`message`를 담아 throw해요.
- `getNavBadges`는 `getTodos()`를 쓰게 바꿔요.
- `frontend/.env.local`에는 `API_URL=http://127.0.0.1:9101`을 넣어요 (예시: `frontend/.env.example`). 도커에서는 `frontend/compose.override.yaml`의 값이 우선이에요.
  - `localhost` 대신 `127.0.0.1`: Node 20 fetch가 `localhost`를 IPv6(`::1`)로 풀면 uvicorn(127.0.0.1)에 연결되지 않아요.
- `try/catch`에서 `unstable_rethrow(e)`를 먼저 불러요. 빌드 중 `no-store` fetch가 던지는 Next 내부 신호(DYNAMIC_SERVER_USAGE)를 삼키면 빌드가 실패해요.
- `getTodos`는 `React.cache`로 묶어요. 레이아웃(배지)과 페이지가 함께 부르는데, `signal` 옵션 때문에 fetch 자동 중복 제거가 안 돼요.
- 캐시 옵션은 `cache: "no-store"`로 정했어요.
  - `cacheComponents`가 꺼져 있으면 옵션 없는 fetch는 `next build` 때 한 번 실행되고 결과가 고정돼요
    (`node_modules/next/dist/docs/01-app/02-guides/caching-without-cache-components.md:111`).
  - 그대로 두면 백엔드가 꺼져 있을 때 build가 실패하고, 켜져 있으면 빌드 시점 값으로 굳어요.
- `signal: AbortSignal.timeout(5000)`으로 백엔드가 응답하지 않을 때 무한 대기를 막아요.
- 에러 화면: `frontend/src/app/admin/error.tsx`(페이지 데이터 실패) + `frontend/src/app/error.tsx`.
  `getNavBadges`는 `admin/layout.tsx`에서 호출돼서 `admin/error.tsx`로는 잡히지 않아요.
- KPI의 매출 `value`/`change`는 `crud/dashboard.py`에서 `revenue_trend`의 마지막 두 달로 `utils.percent_change()`를 써서 계산해요 (CLAUDE.md 원천 데이터 규칙).
- API 연동이 확인되면 `mock-data.ts` 대체 경로를 없애서 mock을 백엔드 하나로 줄여요.
- `.env.example`은 커밋해요. 루트 `.gitignore`의 `!.env.example`이 모든 폴더에 적용돼요.

## 구현 순서와 검증
1. 의존성 추가 → `core/config.py`, `core/clock.py`, `main.py`, `api/main.py`, `api/v1/routes/utils.py` ✅ 2026-10-19 완료
2. `models.py`(→ 이후 `schemas/`로 분리), `crud.py`(→ 이후 `crud/dashboard.py`), `api/v1/routes/dashboard.py`(+ `api/v1/__init__.py`에 include), 테스트 작성 ✅ 2026-10-19 완료 (주문 수 KPI 증감률도 원천 데이터에서 계산: 8.1 → 8.2)
3. pytest, ruff, ty가 통과하는지 확인해요.
4. `/docs`와 curl로 확인해요.
   - 키가 camelCase인지
   - hourly-traffic이 168개인지
   - health-check가 응답하는지
5. `api.ts`를 바꾸고 `/admin`이 기존 화면과 같은지 확인해요(KPI 5.9%, 히트맵, 배지). ✅ 2026-10-19 (주문 수만 8.1 → 8.2, 백엔드 요청 8건씩)
6. `crud/dashboard.py`의 값을 바꾸면 화면에 반영되는지 확인해요. API_URL이 없으면 mock, 백엔드를 끄면 에러가 나는지 확인해요. ✅ 2026-10-19 (백엔드 끔 → error 화면, 켜고 "다시 시도" → 복구. 운영 빌드에서 확인)
7. `npx tsc --noEmit`, `npm run lint`, `npm run build`가 통과하는지 확인해요. ✅ 2026-10-19 (백엔드 끈 상태로 build 통과)
   - 백엔드를 끈 상태에서도 `npm run build`가 통과해야 해요 (빌드 때 fetch하지 않는다는 뜻).
   - 백엔드를 끄고 `/admin`에 들어가면 직접 만든 에러 화면이 나와야 해요.
8. CLAUDE.md를 갱신해요. ✅ 2026-10-19
   - 백엔드 명령어와 구조
   - "`dashboard.ts`와 `schemas/dashboard.py`는 함께 수정" 규칙
   - 스킬 위치 메모
