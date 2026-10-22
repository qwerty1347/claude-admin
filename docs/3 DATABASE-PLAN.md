# MySQL 연동 계획: mock → DB (2026-10-21)

## 작업 순서
단계마다 확인하고 커밋해요.

### 1. 패키지와 DB 연결 기반
- `uv add "sqlalchemy[asyncio]" aiomysql pymysql cryptography alembic`, `uv add --dev ipykernel`
- `app/core/config.py`: `DATABASE_URL`, `database_url_sync`
- `app/core/db.py`: `Base`, `KSTDateTime`, 비동기·동기 엔진과 세션
- `app/api/deps.py`: `AsyncSessionDep`, `SessionDep`
- `app/main.py`: lifespan (종료 시 엔진 정리)
- **확인**: 두 세션으로 `SELECT 1`, 기존 테스트 42개 통과 → 커밋

### 2. 모델과 마이그레이션
- `app/models/`: `customer.py`, `order.py`, `product.py`, `inquiry.py`, `stats.py`, `__init__.py`
  - 기존 `schemas/`, `crud/`와 같은 역할별 패키지 규칙이에요(FastAPI 공식 템플릿 방식).
- `alembic init alembic` → `env.py`에 동기 URL과 `Base.metadata` 연결
- `alembic revision --autogenerate -m "create dashboard tables"` → 생성된 파일 검토
- `alembic upgrade head`
- **확인**: DB 툴에서 테이블 9개, 컬럼, 인덱스, `alembic_version` → 커밋

### 3. 시드
- `app/seeds/dashboard.py`: mock 상수를 옮기고 `seed(session, now)`로 상대 날짜 데이터를 넣어요.
- `uv run python -m app.seeds`
- **확인**: 테이블별 행 수, 오늘 주문 합계 4,120,000, `paid` 12건 등. 다시 실행해도 행 수가 같은지 → 커밋

### 4. crud와 라우트를 DB 조회로 교체
- `app/crud/dashboard.py`: 함수 8개를 `async def ...(session)`로 바꿔 DB에서 조회
- `app/api/v1/routes/dashboard.py`: `async def` + `AsyncSessionDep`
- **확인**: `/api/v1/dashboard/*` 응답 숫자가 지금과 같은지, `/admin` 화면
- 기존 테스트는 테스트 DB가 생기기 전까지 실패할 수 있어서 5단계와 같이 커밋해요.

### 5. 테스트 DB와 테스트
- `backend/.docker/mysql/init/01-create-test-db.sh` + compose 마운트
- `docker compose down -v` → `up -d --build`
  - 볼륨이 새로 만들어지면서 `fastapi_test`가 생겨요.
  - 개발 DB에는 `upgrade head`와 시드를 다시 실행해요.
- `tests/conftest.py`: `fastapi_test` 연결, 테이블 생성, 고정 시각 시드, `clock.now` 고정
- 추가 테스트: `KSTDateTime` 왕복, 시드 재실행, today-revenue와 todos 건수, `alembic upgrade head`
- **확인**: 로컬 `uv run pytest`와 컨테이너 `docker compose exec fastapi uv run pytest` 둘 다 통과, ruff, ty → 커밋 (4단계와 함께)

### 6. 문서
- `2 BACKEND-PLAN.md` 적용 기록, `BACKEND-DEPENDENCIES.md` 패키지, `0 DOCKER-PLAN.md` 마이그레이션·시드·테스트 DB 명령, 이 문서 체크, `CLAUDE.md`, `README.md` → 커밋

### 미리 알아둘 점
- **2단계부터 MySQL 컨테이너가 떠 있어야 해요.**
- **5단계의 `down -v`는 DB 데이터를 지워요.** 그 시점에는 시드 데이터뿐이라 다시 넣으면 돼요.
- **화면이 DB에서 숫자를 읽기 시작하는 건 4단계부터예요.** 그 전까지 화면은 지금처럼 mock으로 동작해요.






## Context
`backend/app/crud/dashboard.py`는 지금 mock 상수를 반환해요. MySQL 9.7 컨테이너(`claude_admin-mysql`, DB `fastapi`)는 떠 있지만 비어 있어요.
mock 데이터를 DB에 넣고, 대시보드 API 8개가 DB에서 읽도록 바꿔요.
- **그대로**: 라우트 경로, 응답 스키마(프론트 계약), 화면 숫자
- **바뀌는 것**: 숫자를 가져오는 곳 (mock 상수 → DB)

규칙은 `2 BACKEND-PLAN.md`의 "DB 접근"과 "타임존"을 따라요.
- SQLAlchemy 2를 써요. API는 비동기 세션, Alembic·시드·노트북은 동기 세션이에요.
- 시각은 KST `DATETIME`으로 저장해요.

## 결정
| 항목 | 결정 | 이유 |
|---|---|---|
| 테이블 구조 | **혼합**: 주문·고객·상품·문의는 원본 테이블, 월별·일별 통계는 집계 테이블 | 원본 테이블은 나중에 주문·상품·회원 메뉴에서 그대로 써요. 통계는 실무 대시보드처럼 미리 계산한 값을 읽어요. 지금 화면 숫자를 그대로 유지할 수 있어요 |
| ORM | SQLAlchemy 2, 비동기(`aiomysql`) + 동기(`pymysql`) | `2 BACKEND-PLAN.md` "DB 접근" |
| 마이그레이션 | Alembic (동기 기본 템플릿) | 마이그레이션은 동기로 충분하고 단순해요 |
| 테스트 DB | 같은 MySQL 안에 `fastapi_test` | 아래 "테스트 DB" |

### 다른 구조와 비교
| 구조 | 장점 | 단점 |
|---|---|---|
| **혼합 (채택)** | 앞으로 쓸 테이블이 생기고 통계는 빠르게 읽음. 숫자 유지 | 집계 테이블은 나중에 배치로 채워야 함 |
| 전부 원본에서 계산 | 가장 정석 | 월 매출 1억 2천만, 주문 3,842건을 맞추려면 주문 수만 건을 생성해야 함 |
| mock 값 그대로 테이블에 | 가장 빠름 | 실제 기능을 붙일 때 다시 설계해야 함 |

## 테이블
### 원본 (실제 업무 데이터)
| 테이블 | 주요 컬럼 | 쓰는 API |
|---|---|---|
| `customers` | id, name, created_at | 주문의 고객 이름 |
| `orders` | id, order_no(unique, `ORD-260930-1042`), customer_id(FK), amount, status, ordered_at, shipped_at(nullable) | recent-orders, today-revenue, todos |
| `products` | id, name, category, stock | todos (재고 부족 상품) |
| `inquiries` | id, customer_id, status(`pending`/`answered`), created_at | todos (답변 대기 문의) |

- `orders.status`: `paid`(결제 완료 = 발송 대기), `shipping`, `delivered`, `cancelled`, `refund_requested`
- 인덱스: `orders.ordered_at`, `orders.status`
- 상태 값은 DB ENUM 대신 `String` + Python `Literal` 검증으로 해요. 값이 바뀔 때 마이그레이션 부담이 적어요.

### 집계 (미리 계산해 둔 통계)
| 테이블 | 주요 컬럼 | 쓰는 API |
|---|---|---|
| `monthly_metrics` | year_month(PK, `2026-09`), revenue, orders, signups, conversion_rate | revenue-trend, kpis(월) |
| `monthly_category_sales` | year_month, category, revenue (PK 두 개) | category-shares |
| `monthly_traffic_sources` | year_month, channel, visitors, sort_order | traffic-sources |
| `hourly_visits` | weekday(0~6), hour(0~23), visits (168행) | hourly-traffic |
| `daily_metrics` | date(PK), orders, signups, conversion_rate, todos_done | kpis(전일·지난주), todos(오늘 처리 건수) |

- 지금은 시드가 집계 테이블을 채워요. 실제 주문이 쌓이면 배치 작업(`entrypoint.sh`의 `worker` 자리)이 `orders`를 집계해서 채워요(예: 매일 새벽).

## 파일
| 파일 | 내용 |
|---|---|
| `app/core/config.py` | `DATABASE_URL: str`(필수), `database_url_sync` property(`make_url(...).set(drivername="mysql+pymysql")`). 시간대 주석을 KST 저장으로 수정 |
| `app/core/clock.py` | docstring을 KST 저장 규칙으로 수정 |
| `app/core/db.py` (새 파일) | `Base`, `KSTDateTime`(TypeDecorator), `async_engine`/`AsyncSessionLocal`, `sync_engine`/`SessionLocal` |
| `app/api/deps.py` | `get_async_session`/`AsyncSessionDep`, `get_session`/`SessionDep` |
| `app/main.py` | lifespan: 종료 시 두 엔진 dispose |
| `app/models/` | `customer.py`, `order.py`, `product.py`, `inquiry.py`, `stats.py`. `__init__.py`에서 전부 import (Alembic이 찾도록) |
| `alembic/`, `alembic.ini` | 마이그레이션 |
| `app/seeds/` | 개발·데모용 시드 (`dashboard.py`에 mock 상수를 옮김, `python -m app.seeds`로 실행) |
| `app/crud/dashboard.py` | async 함수로 DB 조회 |
| `app/api/v1/routes/dashboard.py` | `async def` + `AsyncSessionDep` |
| `.docker/mysql/init/01-create-test-db.sh` | 테스트 DB 생성 |
| `tests/conftest.py` | 테스트 DB 연결, 테이블 생성, 시드, 시각 고정 |

### 엔진·세션 (`app/core/db.py`)
- 엔진 옵션
  - `pool_pre_ping=True`: 끊긴 연결을 감지해요.
  - `pool_recycle=3600`: MySQL `wait_timeout` 전에 다시 연결해요.
- 세션 옵션 `expire_on_commit=False`: commit한 뒤 속성을 읽을 때 다시 조회하지 않아요. 비동기에서는 이게 없으면 에러가 나요.
- `KSTDateTime`
  - 저장할 때 aware datetime에서 tzinfo를 떼서 KST 값으로 넣어요.
  - 읽을 때 `settings.tz`를 붙여서 `+09:00`으로 돌려줘요.
- lifespan에서 dispose하는 이유: TestClient마다 이벤트 루프가 달라서, 종료 때 커넥션 풀을 비우지 않으면 다음 테스트에서 "다른 루프" 에러가 나요.

## 마이그레이션 (Alembic)
```bash
cd backend
uv run alembic init alembic
uv run alembic revision --autogenerate -m "create dashboard tables"   # 생성 결과를 검토한 뒤 커밋
uv run alembic upgrade head
```
- `alembic/env.py`
  - URL은 `settings.database_url_sync`를 써요.
  - `target_metadata = Base.metadata`예요(`import app.models`).
- `alembic.ini`: `post_write_hooks`로 ruff format을 걸어서, 생성된 리비전 파일도 포맷이 맞게 해요.
- 마이그레이션은 entrypoint에서 자동으로 실행하지 않고 명시적으로 실행해요. 서버가 여러 대일 때 동시에 실행되는 문제를 피하려는 실무 관례예요.

## 시드 (`app/seeds/dashboard.py`)
- 함수 모양은 `seed(session, now)`예요. **기준 시각 `now`를 받아서 상대 날짜로** 넣어요.
  - mock은 2026-09-30 기준 스냅샷이에요. DB로 바꾸면 "이번 달", "오늘"이 실제 현재 시각 기준이 돼요.
  - 실행할 때는 `clock.now()`, 테스트할 때는 고정 시각을 넣어요.

| 데이터 | 넣는 값 |
|---|---|
| `monthly_metrics` | now가 속한 달에서 거꾸로 12개월은 mock의 매출·주문 수를 넣어요. 13개월 전 한 달은 전년 동월 매출(104,300,000)이에요. 이번 달과 지난달의 가입자·전환율은 mock 값(1,216/1,256, 3.46/3.06)이에요 |
| 카테고리, 유입 경로 | 이번 달 행 (mock 값) |
| `daily_metrics` | 오늘과 어제는 mock 값(주문 118/109, 가입 37/41, 전환율 3.62/3.41)이에요. 나머지 날짜는 최근 7일 합과 그 전 7일 합이 mock 주간 값(862/905, 281/264, 평균 3.51/3.58)이 되도록 나눠 넣어요. 오늘 `todos_done`은 23이에요 |
| `orders` | 최근 7건은 mock 그대로예요(날짜만 now 기준, 시각은 같음). 보충 주문은 오늘 10:22 이전 합계가 4,120,000, 어제 같은 시각까지 합계가 3,810,000이 되게 넣어요. 상태는 `paid` 12건, `refund_requested` 2건을 맞춰요 |
| `products`, `inquiries` | 재고 10개 미만 상품 3개, 답변 대기 문의 5건 |
| `hourly_visits` | `_hourly_value(h, d)` 168행 |

- 다시 실행해도 같은 결과가 나와요(idempotent). 대상 테이블을 비우고 다시 넣어요.
- 실행: `uv run python -m app.seeds`

## API별 조회 (`app/crud/dashboard.py`)
| API | 읽는 곳 |
|---|---|
| revenue-trend | `monthly_metrics` 최근 12개월 (월 라벨 `"9월"` 형식), 전년 동월은 13개월 전 행 |
| kpis | 월 값은 `monthly_metrics`(이번 달/지난달)에서 읽어요. 비교 값은 `daily_metrics`에서 읽어요(day: 오늘/어제, week: 최근 7일 합/그 전 7일 합, 전환율은 평균). 증감 계산은 지금 `_kpi()`를 재사용해요 |
| category-shares, traffic-sources | 이번 달 행 |
| hourly-traffic | `hourly_visits` (요일 바깥, 시간 안쪽 순서) |
| recent-orders | `orders` + `customers` join, `ordered_at DESC LIMIT 7` |
| todos | `orders` 상태별 COUNT(`paid`, `refund_requested`), `products.stock < 10`, `inquiries.status = 'pending'`, 오늘 `daily_metrics.todos_done` |
| today-revenue | `orders` 합계: [오늘 0시, now) vs [어제 0시, now − 1일) |

- 날짜 경계는 `clock.now()`, `clock.start_of_today()`로 잡아요. `app/utils.py`의 `percent_change`, `round_half_up`은 그대로 써요.
- 라벨, 단위, href, urgent 같은 화면 메타 정보는 crud 상수로 남겨요. 데이터가 아니라 표시 정보라서요.

## 테스트 DB (`fastapi_test`)
같은 MySQL 컨테이너 안에 DB를 하나 더 둬요.
```
claude_admin-mysql
├─ fastapi        개발용. 화면이 읽는 DB. 넣은 데이터가 유지됨
└─ fastapi_test   테스트용. pytest가 실행할 때마다 지우고 새로 채움
```
- **왜 따로 두나**: 테스트는 실행할 때마다 테이블을 지우고 다시 만들어요. 개발 DB에서 돌리면 개발 데이터가 지워져요.
- **실무에서도 흔한 방식**이에요.
  - Rails는 처음부터 `_development`와 `_test`가 따로 설정돼 있어요.
  - Django는 `test_<DB이름>`을 자동으로 만들고 지워요.
  - Laravel은 `.env.testing`으로 따로 지정해요.
  - CI를 붙이면 그때는 테스트할 때마다 빈 MySQL 컨테이너를 새로 띄우는 방식도 같이 써요.
- **SQLite를 쓰지 않는 이유**: 운영 DB가 MySQL이라서 문자셋, 시간대, 드라이버 차이로 "테스트는 통과했는데 운영에서 깨지는" 일이 생길 수 있어요.

### 만드는 방법
- `backend/.docker/mysql/init/01-create-test-db.sh`
  - `CREATE DATABASE fastapi_test` (`utf8mb4_unicode_ci`)
  - `GRANT ALL ON fastapi_test.* TO '$MYSQL_USER'@'%'`
  - 사용자 이름은 환경변수로 받아요. `.sh`는 `.gitattributes`로 LF가 보장돼요.
- `backend/compose.yaml` mysql에 `./.docker/mysql/init:/docker-entrypoint-initdb.d:ro` 마운트를 추가해요.
- init 스크립트는 **볼륨이 비어 있을 때만** 실행돼요. 그래서 처음 한 번 `docker compose down -v`를 해요. 지금은 DB가 비어 있어서 잃을 데이터가 없어요.

### conftest.py
- app을 import하기 전에 `settings.DATABASE_URL`의 DB 이름을 `<이름>_test`로 바꿔요. 로컬(`127.0.0.1`)과 컨테이너(`mysql`) 둘 다 동작해요.
- session fixture
  - 동기 엔진으로 `Base.metadata.drop_all/create_all`을 실행해요.
  - `seed(session, now=FIXED_NOW)`로 넣어요. FIXED_NOW는 `2026-09-30 13:50 KST`예요.
- `clock.now`를 FIXED_NOW로 고정해요. 그래서 **기존 기대값(5.9, 8.2, `2026-09-30T13:42:00+09:00`, -3.2, 0.4 등)이 그대로** 통과해야 해요.
- 추가 테스트
  - `KSTDateTime` 왕복 (저장 → 읽기에서 `+09:00` 유지)
  - 시드를 두 번 실행해도 행 수가 같은지
  - today-revenue 합계, todos 건수
  - 빈 DB에서 `alembic upgrade head`가 성공하는지 (마이그레이션과 모델이 어긋나지 않았는지)
- 쓰기 API(주문 생성 등)가 생기면 테스트마다 트랜잭션 롤백 방식을 추가해요.

## 패키지
```bash
cd backend
uv add "sqlalchemy[asyncio]" aiomysql pymysql cryptography alembic
uv add --dev ipykernel     # 노트북 커널 복구 (.venv 재생성 때 사라짐)
```
- 패키지를 바꾼 뒤 도커는 `docker compose up -d --build -V fastapi`로 다시 만들어요.

## 실행 순서 (적용 후, 루트에서)
```bash
docker compose down -v                                         # 처음 한 번 (테스트 DB init 스크립트 실행용)
docker compose up -d --build
docker compose exec fastapi uv run alembic upgrade head        # 테이블 생성
docker compose exec fastapi uv run python -m app.seeds  # 시드
```

## 확인 방법
1. DB 툴로 테이블과 행 수를 확인해요. `orders.ordered_at`이 KST 값인지도 봐요.
2. `docker compose exec fastapi uv run pytest -q`와 로컬 `cd backend && uv run pytest`
   - 기존 42개와 새 테스트가 통과해야 해요. ruff, ty도 통과해야 해요.
3. `/admin` 화면을 확인해요.
   - 숫자가 지금과 같아야 해요(매출 1억 2,845만, 5.9%, 주문 8.2%, 오늘 412만, 처리할 일 12/2/3/5).
   - 월 라벨만 실행 날짜 기준으로 바뀌어요(지금이면 "11월~10월").
4. fastapi 로그에 SQL 에러가 없는지 봐요. 백엔드를 끄면 error.tsx 화면이 나와야 해요.
