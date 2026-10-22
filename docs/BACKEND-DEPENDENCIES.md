# 백엔드 의존성과 pyproject.toml 설명 (2026-10-21)

`backend/pyproject.toml` 한 파일에 **패키지 목록**(`[project]`, `[dependency-groups]`)과 **도구 설정**(`[tool.*]`)이 같이 있어요.
Laravel로 치면 `composer.json`에 `phpunit.xml`, `pint.json` 같은 설정을 한데 모은 파일이에요.

| 파일 | 역할 | Laravel / npm |
|---|---|---|
| `pyproject.toml` | 필요한 패키지와 허용 버전 범위(`>=`), 도구 설정 | `composer.json` / `package.json` |
| `uv.lock` | 실제로 설치되는 **정확한 버전**과 해시. 직접 고치지 않아요 | `composer.lock` / `package-lock.json` |
| `.python-version` | Python 버전(3.12). uv가 보고 맞는 Python을 써요 | `.nvmrc` |
| `.venv/` | 설치된 패키지가 들어가는 가상환경. 커밋하지 않아요 | `vendor/` / `node_modules/` |

## [project]: 앱 정보와 운영 패키지
```toml
[project]
name = "claude-admin-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.143.0",
    "pydantic-settings>=2.15.0",
    "tzdata>=2026.5",
]
```
- `requires-python`: 이 앱은 Python 3.12 이상에서 돌아가요.
- `dependencies`: **앱 실행에 필요한 패키지**예요. 운영 서버와 도커 `prod` 이미지에도 설치돼요.

| 패키지 | 설치 버전 (uv.lock) | 쓰는 이유 |
|---|---|---|
| `fastapi[standard]` | 0.143.0 | 웹 프레임워크. `[standard]`는 "자주 쓰는 부가 패키지도 같이 설치"라는 뜻(아래 표) |
| `pydantic-settings` | 2.15.0 | `.env`와 환경변수를 `Settings` 클래스로 읽어요 (`app/core/config.py`) |
| `tzdata` | 2026.5 | 시간대 데이터. Windows에는 OS 시간대 DB가 없어서, 없으면 `ZoneInfo("Asia/Seoul")`가 `ZoneInfoNotFoundError`를 내요 |

### fastapi[standard]가 같이 설치하는 것
| 패키지 | 설치 버전 | 역할 |
|---|---|---|
| `fastapi-cli` | 0.0.32 | `fastapi dev`, `fastapi run` 명령 |
| `uvicorn` | 0.54.0 | 실제로 요청을 받는 ASGI 서버 (`fastapi dev`가 내부에서 실행) |
| `httpx` | 0.28.1 | HTTP 클라이언트. 테스트의 `TestClient`와 외부 API 호출에 써요 |
| `pydantic-settings` | 2.15.0 | 위와 같음 (직접 의존성으로도 적어 둬서 명시적으로 관리해요) |
| `python-multipart` | | 폼·파일 업로드 요청 파싱 |
| `email-validator` | 2.3.0 | Pydantic `EmailStr` 검증 |
| `jinja2` | | 템플릿 (HTML 응답이 필요할 때) |
| `pydantic-extra-types` | | 전화번호, 색상 같은 추가 타입 |
| `opentelemetry-*`, `fastar` | | FastAPI 쪽에서 standard에 포함한 부가 패키지 (지금 코드에서는 직접 쓰지 않아요) |

- 같이 설치되는 핵심 라이브러리: `starlette` 1.7.0 (FastAPI의 기반), `pydantic` 2.14.1 (데이터 검증, 스키마)
- 전체 설치 패키지 수는 `uv.lock` 기준 65개예요. 트리는 `uv tree`로 볼 수 있어요.

## [dependency-groups]: 개발용 패키지
```toml
[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "ruff>=0.17.1",
    "ty>=0.0.89",
]
```
**개발할 때만 쓰는 패키지**예요. Laravel `require-dev`, npm `devDependencies`와 같아요.

| 패키지 | 설치 버전 | 역할 |
|---|---|---|
| `pytest` | 9.1.1 | 테스트 실행 (`tests/`) |
| `ruff` | 0.17.1 | 린트(`ruff check`)와 포맷(`ruff format`) |
| `ty` | 0.0.89 | 타입 검사 (mypy 같은 역할, ruff를 만든 Astral의 도구) |

| | `[project] dependencies` | `[dependency-groups] dev` |
|---|---|---|
| 내용 | 앱 실행에 필요 | 개발 중에만 필요 |
| 로컬 `uv sync` | 설치 | 설치 (기본 포함) |
| 도커 `dev` 이미지 (`uv sync --locked`) | 설치 | 설치 → 컨테이너에서 pytest 가능 |
| 도커 `prod` 이미지 (`uv sync --locked --no-dev`) | 설치 | **설치 안 함** → 이미지가 가볍고 쓸 일 없는 도구가 서버에 없음 |
| 추가 명령 | `uv add <pkg>` | `uv add --dev <pkg>` |

- 그룹 이름 `dev`는 관례예요. 필요하면 `docs = [...]`처럼 그룹을 더 만들 수 있어요.

## 버전 표기
- `>=0.143.0`: "0.143.0 이상"이라는 **허용 범위**예요.
- 실제 설치 버전은 `uv.lock`에 고정돼 있어요. 그래서 어느 PC, 어느 도커 이미지에서든 같은 버전이 설치돼요.
- `uv.lock`은 `uv add`, `uv lock --upgrade` 같은 명령이 갱신해요. **`pyproject.toml`과 `uv.lock`은 항상 같이 커밋해요.**

## [tool.*]: 도구 설정
### [tool.fastapi]
```toml
entrypoint = "app.main:app"
```
- `fastapi dev` / `fastapi run`이 실행할 앱이에요. `app/main.py` 파일의 `app` 변수(`app = FastAPI(...)`)를 가리켜요.
- 그래서 경로 없이 `uv run fastapi dev`만 쳐도 돼요. `backend/.docker/entrypoint.sh`도 이 설정을 써요.
- fastapi-tistory의 `uvicorn app.main:app`에서 `app.main:app`을 설정으로 뺀 것과 같아요.

### [tool.pytest.ini_options]
```toml
pythonpath = ["."]
```
- pytest가 실행될 때 `backend/`를 import 경로에 추가해요. 그래야 테스트에서 `from app.main import app`이 돼요.
- 없으면 `ModuleNotFoundError: No module named 'app'`이 나요.

### [tool.ruff]
```toml
target-version = "py312"
```
- ruff에게 이 코드가 Python 3.12용이라고 알려줘요. 3.12 문법(`class ApiResponse[T]`, `datetime.UTC`)을 기준으로 검사하고 권해요.
- `.python-version`(3.12), Dockerfile의 `python:3.12-slim`과 맞춘 값이에요.

### [tool.ruff.lint]
FastAPI 공식 템플릿(full-stack-fastapi-template)의 설정을 기준으로 했어요.

**select (켜는 규칙)**
| 코드 | 이름 | 잡아내는 것 (예) |
|---|---|---|
| `E` | pycodestyle errors | 들여쓰기·공백 같은 PEP 8 스타일 오류 |
| `W` | pycodestyle warnings | 줄 끝 공백, 파일 끝 빈 줄 |
| `F` | pyflakes | 안 쓰는 import·변수, 정의 안 된 이름 |
| `I` | isort | import 순서 (표준 라이브러리 → 외부 패키지 → 내 코드) |
| `B` | flake8-bugbear | 버그가 되기 쉬운 코드. 예: `def f(x=[])` (기본값 리스트가 호출 사이에 공유됨) |
| `C4` | flake8-comprehensions | `list([x for x in ...])` 같은 불필요한 감싸기 |
| `UP` | pyupgrade | 옛 문법을 최신 문법으로. 예: `Optional[int]` → `int \| None`, `timezone.utc` → `UTC` |
| `ARG001` | unused arguments | 함수에서 안 쓰는 인자 (그래서 예외 핸들러 인자에 `_request`처럼 `_`를 붙였어요) |
| `FAST` | FastAPI | FastAPI 전용 규칙. 예: `Depends`를 `Annotated` 없이 쓰는 것, 불필요한 `response_model` |

**ignore (끄는 규칙)**
| 코드 | 끄는 이유 |
|---|---|
| `E501` | 한 줄 길이 제한. 줄바꿈은 `ruff format`이 맡아서 중복이에요 |
| `B008` | "기본값에서 함수 호출 금지". FastAPI는 `Query()`, `Depends()`를 기본값 자리에 쓰는 게 정상이에요 |
| `W191` | 탭 들여쓰기 경고. 포매터와 겹쳐요 |
| `B904` | `except` 안에서 `raise ... from e`를 강제하는 규칙. `HTTPException`을 그냥 던지는 FastAPI 관례 때문에 꺼요 |

## 자주 쓰는 명령 (`backend/`에서)
| 하고 싶은 것 | 명령 |
|---|---|
| 설치 / `.venv` 만들기 | `uv sync` |
| 운영 패키지 추가 | `uv add <pkg>` |
| 개발 패키지 추가 | `uv add --dev <pkg>` |
| 제거 | `uv remove <pkg>` |
| 하나만 업그레이드 | `uv lock --upgrade-package <pkg> && uv sync` |
| 전부 업그레이드 | `uv lock --upgrade && uv sync` |
| 의존성 트리 보기 | `uv tree` |
| 테스트·린트·타입 검사 | `uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run ty check` |
| 자동 수정 | `uv run ruff check . --fix && uv run ruff format .` |

- 도커에서는 루트에서 `docker compose exec fastapi uv add <pkg>`처럼 써요.
- 패키지를 바꾼 뒤에는 `docker compose up -d --build -V fastapi`로 이미지를 다시 만들어요(`0 DOCKER-PLAN.md`).
- 컨테이너에서 추가했다면 로컬에서도 `uv sync`를 한 번 해요. VS Code 자동완성은 로컬 `.venv`를 봐요.

## 앞으로 추가할 패키지 (계획)
| 시점 | 패키지 | 이유 |
|---|---|---|
| DB 연동 | `sqlalchemy[asyncio]`, `aiomysql`, `pymysql`, `cryptography`, `alembic` | ORM(비동기+동기), MySQL 드라이버 2개, MySQL 9 인증, 마이그레이션 (`2 BACKEND-PLAN.md` "DB 접근") |
| 노트북 | `ipykernel` (dev) | `pyproject.toml`에 없어서 `.venv`를 새로 만들면 사라져요(2026-10-21 폴더 이름 변경 때 실제로 사라짐). `uv add --dev ipykernel`로 등록하면 `uv sync` 때마다 같이 설치돼요 |
