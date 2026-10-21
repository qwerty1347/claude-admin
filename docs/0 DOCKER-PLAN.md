# 모노레포 + 도커 개발·배포 환경 (2026-10-20 계획, 2026-10-21 적용)

## Context
처음에는 한 저장소(`claude-admin`)의 루트에 Next가 있고, FastAPI는 `backend/`에 있었어요. 둘 다 로컬에서 각각 띄웠어요(3001, 9101).
- 다른 PC에서 작업하려면 Node, uv, (나중에) DB를 다시 설치해야 했어요.
- 원하는 모습
  - **git 저장소는 하나**: push하는 곳이 한 곳 (GitHub `qwerty1347/claude-admin` 그대로)
  - **로컬은 프로젝트별로**: `frontend/`와 `backend/`가 각자 독립 프로젝트예요. 각자 VS Code 창, 각자 compose가 있어서 그 폴더에서 `docker compose up`을 하면 그 프로젝트만 떠요.
  - **한 번에 실행도 가능**: 루트에서 `docker compose up`을 하면 Docker Desktop에 `claude-admin` 묶음 하나로 컨테이너 3개가 떠요.
- 그래서 **모노레포(저장소 하나, 하위 폴더 둘) + 폴더별 compose + 루트 include** 구조로 했어요.
- 개발용과 배포용은 처음부터 나눠요. 실무 표준 방식(compose base + override + prod, Dockerfile multi-stage, 환경별 env)을 써요.

## 구조
```
claude-admin\                      git 저장소 1개 (push 한 곳)
├─ compose.yaml                    전체 실행 (개발): 두 프로젝트를 include, 프로젝트 이름 claude-admin
├─ compose.prod.yaml               전체 실행 (배포)
├─ CLAUDE.md  README.md
├─ .gitignore                      공통(.env 등)만
├─ .gitattributes                  *.sh 는 LF 고정
├─ docs\                           0~3 문서
├─ frontend\                       ← 로컬 프로젝트 1 (Next). 서비스 이름 nextjs
│  ├─ compose.yaml                 공통
│  ├─ compose.override.yaml        개발 (docker compose up 이 자동으로 합침)
│  ├─ compose.prod.yaml            배포
│  ├─ .docker\Dockerfile           multi-stage (dev / build / prod)
│  ├─ .dockerignore  .gitignore
│  ├─ .env.example (커밋)  .env.local (커밋 X)
│  └─ src\ public\ package.json package-lock.json next.config.ts tsconfig.json
│     eslint.config.mjs postcss.config.mjs AGENTS.md
└─ backend\                        ← 로컬 프로젝트 2 (FastAPI). 서비스 이름 fastapi, mysql
   ├─ compose.yaml  compose.override.yaml  compose.prod.yaml
   ├─ .docker\Dockerfile           multi-stage (dev / prod)
   ├─ .docker\entrypoint.sh        SERVICE_TYPE, ENVIRONMENT 로 실행 명령 선택
   ├─ .dockerignore  .gitignore
   ├─ .env.example (커밋)  .env (커밋 X)
   └─ app\ tests\ notebooks\ pyproject.toml uv.lock .python-version
```
- **폴더 이름**(`frontend/`, `backend/`)과 **compose 서비스·컨테이너 이름**(`nextjs`, `fastapi`, `claude_admin-*`)은 달라요. 명령에서 쓰는 건 서비스 이름이에요(`docker compose exec fastapi ...`).
- 하위 폴더만 열어도 VS Code가 상위 `.git`을 찾아서 Source Control이 그대로 동작해요.
- `backend\`를 루트로 열면 Pylance가 `.venv`를 바로 찾아요. 그래서 루트 `pyrightconfig.json`은 지웠어요.
- Claude Code는 실행한 폴더부터 상위 폴더까지 `CLAUDE.md`를 읽어요. 하위 폴더에서 작업해도 루트 규칙이 적용돼요.
- compose 파일 이름은 Compose 공식 기본 이름(`compose.yaml`)이에요. `docker-compose.yml`도 읽히지만 예전 이름이에요.

## 전체 실행 (루트 compose, include)
```
Docker Desktop > Containers
▼ claude-admin                  ← compose 프로젝트 1개
    claude_admin-nextjs         ← 컨테이너
    claude_admin-fastapi
    claude_admin-mysql
```

```yaml
# compose.yaml (개발)                     # compose.prod.yaml (배포)
name: claude-admin                        name: claude-admin
include:                                  include:
  - path:                                   - path:
      - backend/compose.yaml                    - backend/compose.yaml
      - backend/compose.override.yaml           - backend/compose.prod.yaml
  - path:                                   - path:
      - frontend/compose.yaml                   - frontend/compose.yaml
      - frontend/compose.override.yaml          - frontend/compose.prod.yaml
```
- `include`는 Compose 공식 기능이에요(2.20 이상, 이 PC는 2.34).
  - 포함된 파일의 상대 경로(`./`, `.docker/Dockerfile`)와 `.env`는 그 파일이 있는 폴더 기준으로 읽혀요.
- `include`는 지정한 파일만 읽어요. 그래서 개발용(`override`)과 배포용(`prod`)을 짝으로 적어요.
- 각 폴더에서 따로 띄울 수도 있어요(`backend/`에서 `docker compose up -d`). 이때는 Docker Desktop에 `backend` 묶음으로 보여요.
  - 루트 실행과 폴더 실행은 동시에 쓰지 않아요. `container_name`이 같아서 이름 충돌 에러가 나요. 바꿀 때는 먼저 `down` 해요.

## git 사용
- **push는 한 번**이에요. 두 폴더를 같이 고쳤으면 커밋 하나로 묶을 수도 있어요.
- **한 프로젝트만 받기**: `sparse-checkout`
  ```bash
  git clone --filter=blob:none --sparse https://github.com/qwerty1347/claude-admin.git
  cd claude-admin
  git sparse-checkout set backend      # 작업 폴더에는 backend/ (+ 루트 파일)만
  git sparse-checkout add frontend     # 나중에 추가
  git sparse-checkout disable          # 전부 받기
  ```
- **한 프로젝트 기록만 보기**: `git log -- backend/`
- **커밋 메시지**: 어느 쪽 변경인지 접두어를 붙여요. 예: `[backend] 주문 API 추가`, `[frontend] KPI 티커`
- **배포 자동화(나중에)**: GitHub Actions에서 `paths: ["backend/**"]`처럼 경로 필터를 걸어, 바뀐 프로젝트만 빌드하고 배포해요.

## 개발 / 배포 차이
| | 개발 (`compose.yaml` + `compose.override.yaml`) | 배포 (`compose.yaml` + `compose.prod.yaml`) |
|---|---|---|
| Dockerfile stage | `dev` | `prod` |
| 실행 | `next dev`, `fastapi dev` (hot reload) | `node server.js`, `fastapi run` (빌드 결과) |
| 소스 | 바인드 마운트 (저장하면 바로 반영) | 이미지에 포함 (마운트 없음) |
| 패키지 | dev 포함 (eslint, pytest, ruff, ty) | 운영에 필요한 것만 |
| 실행 계정 | root (기본) | 일반 사용자 |
| 재시작 | 없음 | `restart: unless-stopped` |
| DB 포트 | 호스트에 공개 (3306, DB 툴 접속용) | 공개 안 함 |
| 비밀값 | `.env` (`.env.example` 복사) | 서버의 `.env` 또는 배포 도구 Secrets |

## 포트와 연결
| 폴더 | 서비스 | container_name | 호스트 → 컨테이너 |
|---|---|---|---|
| `frontend/` | `nextjs` | `claude_admin-nextjs` | 3001 → 3001 |
| `backend/` | `fastapi` | `claude_admin-fastapi` | 9101 → 8000 |
| `backend/` | `mysql` | `claude_admin-mysql` | 3306 → 3306 (개발만. XAMPP MySQL과 같은 포트라 동시에 켜지 않음) |

- **nextjs → fastapi**: 폴더별 compose는 서로 다른 프로젝트라서 서비스 이름으로는 못 불러요. 호스트에 열린 백엔드 포트로 불러요.
  - 개발: `API_URL=http://host.docker.internal:9101`
    - Docker Desktop(Windows, Mac)은 이 주소를 기본으로 지원해요. Linux에서도 되도록 `extra_hosts: host.docker.internal:host-gateway`를 넣었어요.
    - 백엔드를 도커로 띄웠든 로컬(`uv run fastapi dev --port 9101`)로 띄웠든 같은 주소라서 섞어 써도 돼요. 루트 include로 묶어 띄워도 같은 주소를 써요.
  - 배포: 서버 환경변수로 실제 API 주소를 넣어요. 예: `API_URL=https://api.example.com`
- **fastapi → mysql**: 같은 compose라서 서비스 이름 `mysql:3306`으로 불러요.
- **env 규칙**
  - 각 프로젝트의 env 파일(`frontend/.env.local`, `backend/.env`)에는 로컬 방식 값을 넣어요(`127.0.0.1:9101`, `127.0.0.1:3306`).
  - 도커에서는 compose의 `environment`가 그 값을 덮어써요(`host.docker.internal:9101`, `mysql:3306`).
  - Next와 pydantic-settings 둘 다 이미 있는 환경변수를 env 파일로 덮지 않아요. 그래서 파일을 고치지 않아도 두 방식을 다 쓸 수 있어요.

## frontend/

### .docker/Dockerfile
Next 공식 Docker 예시(standalone 출력) 구조예요.
```dockerfile
FROM node:24-slim AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

FROM deps AS dev                 # 개발: override 에서 소스 마운트, next dev
COPY . .
CMD ["npm", "run", "dev"]

FROM deps AS build
COPY . .
RUN npm run build

FROM base AS prod                # 배포: 빌드 결과만, 일반 사용자로 실행
ENV NODE_ENV=production PORT=3001 HOSTNAME=0.0.0.0
COPY --from=build /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
CMD ["node", "server.js"]
```
- `next.config.ts`에 `output: "standalone"`을 넣었어요. 배포 이미지에 필요한 파일만 담겨요.

### compose
```yaml
# compose.yaml (공통)
services:
  nextjs:
    build: { context: ., dockerfile: .docker/Dockerfile }
    container_name: claude_admin-nextjs

# compose.override.yaml (개발)
services:
  nextjs:
    build: { target: dev }
    ports: ["3001:3001"]
    volumes:
      - ./:/app
      - /app/node_modules              # 컨테이너(Linux)용 패키지. 호스트 것으로 덮이지 않게
      - /app/.next
    environment:
      API_URL: http://host.docker.internal:9101
      WATCHPACK_POLLING: "true"        # Windows 마운트에서 변경 감지
    extra_hosts: ["host.docker.internal:host-gateway"]

# compose.prod.yaml (배포)
services:
  nextjs:
    build: { target: prod }
    restart: unless-stopped
    ports: ["3001:3001"]               # 앞단 Nginx/Caddy(HTTPS)가 여기로 전달
    environment:
      API_URL: ${API_URL:?...}         # 서버 환경변수 필수. 예: https://api.example.com
```
(실제 파일은 블록 형식으로 적혀 있어요. 여기서는 줄여서 보여 줘요.)

### .env.example, .dockerignore
- `.env.example`: `API_URL=http://127.0.0.1:9101` (로컬 방식용. `.env.local`로 복사)
- `.dockerignore`: `node_modules`, `.next`, `.env*`, `.playwright-mcp`

## backend/

### .docker/Dockerfile
```dockerfile
FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.10.6 /uv /uvx /bin/   # uv 설치 (공식 이미지에서 복사, 버전 고정)
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=0 PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY --chmod=755 .docker/entrypoint.sh /entrypoint.sh   # 소스 마운트(/app) 바깥
ENTRYPOINT ["/entrypoint.sh"]

FROM base AS dev                 # 개발: dev 의존성 포함
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-install-project
COPY . .

FROM base AS prod                # 배포: 운영 의존성만, 일반 사용자로 실행
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY . .
RUN uv sync --locked --no-dev
RUN useradd --system --no-create-home app
USER app
```
- 의존성 파일을 코드보다 먼저 복사해요. 코드만 바뀐 빌드에서는 설치 단계가 캐시돼요.

### .docker/entrypoint.sh (fastapi-tistory 방식)
```sh
case "$SERVICE_TYPE" in
    app)
        if [ "$ENVIRONMENT" = "local" ]; then
            exec uv run fastapi dev --host 0.0.0.0 --port 8000   # 개발 (hot reload)
        else
            exec fastapi run --host 0.0.0.0 --port 8000          # 배포
        fi ;;
    # worker) exec uv run arq app.worker.WorkerSettings ;;       # 백그라운드 작업이 생기면
    *) echo "ERROR: SERVICE_TYPE ..." ; exit 1 ;;
esac
```
- `SERVICE_TYPE: app`은 `compose.yaml`에서, `ENVIRONMENT=local`은 `.env`에서, `ENVIRONMENT: production`은 `compose.prod.yaml`에서 정해요.
- `--host 0.0.0.0`이 꼭 필요해요. 기본값이 127.0.0.1이라서, 빠뜨리면 컨테이너 밖에서 접속이 안 돼요.
- `.gitattributes`(`*.sh text eol=lf`)로 LF를 고정해요. 이 PC는 `core.autocrlf=true`라서, 없으면 CRLF로 바뀌어 Linux에서 실행되지 않아요.
- 스크립트는 `/app` 바깥에 복사돼서 소스 마운트가 덮어쓰지 않아요. 그래서 이 파일을 고친 뒤에는 `--build`가 필요해요.

### compose
```yaml
# compose.yaml (공통). ${DB_*} 는 같은 폴더의 .env 에서 읽음
services:
  fastapi:
    build: { context: ., dockerfile: .docker/Dockerfile }
    container_name: claude_admin-fastapi
    env_file: .env
    environment:
      SERVICE_TYPE: app
      DATABASE_URL: mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}?charset=utf8mb4
    depends_on:
      mysql: { condition: service_healthy }

  mysql:
    image: mysql:9.7
    container_name: claude_admin-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      TZ: Asia/Seoul
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    volumes: ["mysql_data:/var/lib/mysql"]
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -u root -p$$MYSQL_ROOT_PASSWORD --silent"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 20s
volumes:
  mysql_data:

# compose.override.yaml (개발)
services:
  fastapi:
    build: { target: dev }
    ports: ["9101:8000"]
    volumes:
      - ./:/app
      - /app/.venv                     # 컨테이너(Linux)용 가상환경. 호스트 .venv 로 덮이지 않게
    environment:
      WATCHFILES_FORCE_POLLING: "true"
  mysql:
    ports: ["3306:3306"]               # DB 툴, 로컬 방식 백엔드 접속용

# compose.prod.yaml (배포)
services:
  fastapi:
    build: { target: prod }
    restart: unless-stopped
    ports: ["9101:8000"]
    environment:
      ENVIRONMENT: production
      FRONTEND_HOST: ${FRONTEND_HOST}  # 예: https://admin.example.com
  mysql:
    restart: unless-stopped            # ports 없음: DB 는 외부에 열지 않음
```

### .env.example (커밋)
```dotenv
ENVIRONMENT=local
FRONTEND_HOST=http://localhost:3001
TIMEZONE=Asia/Seoul

# compose 가 mysql 컨테이너를 만들 때 쓰는 값 (개발 전용)
DB_NAME=fastapi
DB_USER=admin
DB_PASSWORD=admin
DB_ROOT_PASSWORD=root

# 로컬 방식(uv run fastapi dev)용. 도커에서는 compose 가 mysql:3306 으로 덮어씀
DATABASE_URL=mysql+aiomysql://admin:admin@127.0.0.1:3306/fastapi?charset=utf8mb4
```
- 개발 DB 접속 정보: DB `fastapi`, 사용자 `admin` / `admin`, root `root`
  - 호스트(DB 툴)에서는 `127.0.0.1:3306`, 컨테이너 안에서는 `mysql:3306`이에요.
- 개발 값은 커밋해도 돼요. 운영 값은 서버의 `.env`나 배포 도구(GitHub Actions Secrets 등)로 넣어요.
- `.dockerignore`: `.venv`, `__pycache__`, `.ruff_cache`, `.pytest_cache`, `.env`, `notebooks`

## 사용법
| 하고 싶은 것 | 위치 | 명령 |
|---|---|---|
| 전부 띄우기 (개발) | 루트 | `docker compose up -d` |
| 전부 끄기 | 루트 | `docker compose down` (DB 데이터 유지, `-v`를 붙이면 삭제) |
| 일부만 | 루트 | `docker compose up -d fastapi mysql` |
| 한 프로젝트만 | `frontend/` 또는 `backend/` | `docker compose up -d` (루트 실행과 동시에 쓰지 않음) |
| DB만 띄우고 백엔드는 로컬 | 루트 | `docker compose up -d mysql` → `cd backend && uv run fastapi dev --port 9101` |
| 로그 | 루트 | `docker compose logs -f fastapi` / `nextjs` |
| 테스트·린트 | 루트 | `docker compose exec fastapi uv run pytest -q` (ruff, ty도 같은 식), `docker compose exec nextjs npm run lint` |
| 컨테이너 셸 | 루트 | `docker compose exec fastapi bash` |
| 패키지 추가 | 루트 | `docker compose exec fastapi uv add <pkg>` → `docker compose up -d --build -V fastapi` (nextjs는 `npm install <pkg>`) |
| 배포 이미지로 띄우기 | 루트 | `docker compose -f compose.prod.yaml up -d --build` |

### 무엇을 고쳤을 때 무엇을 하나
| 고친 것 | 할 일 |
|---|---|
| 코드 (`app/`, `src/`) | 없음. 마운트와 hot reload로 바로 반영 |
| `.env` 값, compose 파일 (포트, 환경변수) | `docker compose up -d` (compose가 바뀐 컨테이너만 다시 만들어요) |
| Dockerfile, `entrypoint.sh` | `docker compose up -d --build` |
| 패키지 목록 (`pyproject.toml`/`uv.lock`, `package.json`/`package-lock.json`) | `docker compose up -d --build -V` (`-V`: 익명 볼륨 `.venv`/`node_modules`를 새로 만들어요) |
| compose에서 서비스를 지움 | `docker compose up -d --remove-orphans` |
| MySQL 초기값 (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, 문자셋) | 볼륨이 처음 만들어질 때만 적용돼요. `docker compose down -v` 후 `up -d` (데이터 삭제) 또는 `ALTER USER`로 직접 변경 |

- 패키지를 컨테이너 안에서 추가했다면 로컬에서도 `uv sync` / `npm install`을 해요. VS Code 자동완성은 로컬 `.venv`/`node_modules`를 봐요.
- `docker compose restart`는 껐다 켜기만 해요. 설정 변경은 반영되지 않아요.

## DB: MySQL 9.7
- **버전**: 2026-10-20 기준 `lts` 태그가 9.7.2예요. 운영 DB는 LTS가 기본이라 `mysql:9.7`을 써요. 9.7.x 패치는 자동으로 따라가요.
  - `latest`는 26.7 Innovation 버전이에요. 다음 릴리스가 나오면 지원이 끝나서 운영에는 쓰지 않아요.
- **문자셋: `utf8mb4` / `utf8mb4_unicode_ci`** (fastapi-tistory와 같음)
  - 한글과 이모지가 모두 저장돼요. `utf8`(= `utf8mb3`)은 이모지가 저장되지 않아서 쓰지 않아요.
  - `unicode_ci`는 Laravel 기본값이기도 하고, 다른 DB와 데이터를 주고받을 때 호환이 편해요. MySQL 9 기본값은 `utf8mb4_0900_ai_ci`예요.
  - 앱 접속 URL에도 `?charset=utf8mb4`를 붙여요.
- **시간대: Asia/Seoul**
  - 컨테이너 환경변수 `TZ: Asia/Seoul`로 설정해요. MySQL `time_zone` 기본값이 `SYSTEM`이라 서버 시간(KST)을 따라가요.
  - `--default-time-zone=Asia/Seoul` 옵션은 쓰지 않아요. 첫 초기화 때는 시간대 테이블이 없어서 `Unknown or incorrect time zone` 에러로 뜨지 않을 수 있어요.
  - 앱도 `clock.now()`(KST)로 `DATETIME` 컬럼에 저장해요. 규칙은 `2 BACKEND-PLAN.md` 타임존 섹션에 있어요.
- **인증**
  - 기본 `caching_sha2_password`를 써요. `mysql_native_password` 옵션은 MySQL 9에서 없어져서, 넣으면 컨테이너가 뜨지 않아요.
  - aiomysql과 PyMySQL은 이 인증 방식에 `cryptography`가 필요해요.
  - DBeaver 등 JDBC 클라이언트에서 `Public Key Retrieval is not allowed`가 나오면 드라이버 속성 `allowPublicKeyRetrieval=true`를 켜요(개발용).
- **데이터 위치**: named volume `claude-admin_mysql_data` (Docker Desktop > Volumes). 프로젝트 폴더에는 파일이 생기지 않아요. 컨테이너를 지우거나 다시 빌드해도 남고, `down -v`를 할 때만 지워져요.
  - 백업: `docker compose exec mysql mysqldump -u root -proot fastapi > backup.sql`
- **운영**: 서버 한 대라면 위 compose로 띄우고 정기 백업을 해요. 규모가 커지면 관리형 DB(AWS RDS 등)로 옮기고 `DATABASE_URL`만 바꿔요.
- **ORM: SQLAlchemy 2, 비동기 + 동기 둘 다** (자세한 규칙은 `2 BACKEND-PLAN.md`의 "DB 접근")
  - 비동기 `mysql+aiomysql`은 API 라우트 기본이에요. 동기 `mysql+pymysql`은 Alembic, 시드, 스크립트, 노트북, 동기 라우트에서 써요.
  - 접속 정보는 `DATABASE_URL` 하나(aiomysql)만 두고, 동기 URL은 드라이버 이름만 바꿔서 만들어요.
  - `uv add "sqlalchemy[asyncio]" aiomysql pymysql cryptography alembic`

## 주의할 점
- **Node 버전**
  - Node 20은 2026-04-30에 지원이 끝났어요(EOL). 도커 이미지는 현재 LTS인 `node:24`를 써요.
  - 로컬 Node는 아직 20.15예요. 24로 올리고, `frontend/package.json`에 `"engines": { "node": ">=24" }`와 `frontend/.nvmrc`(`24`)를 둬요. `@types/node`도 `^24`로 맞춰요.
  - node:24에 들어 있는 npm 11은 패키지 설치 스크립트를 기본으로 막아요(빌드 로그의 `install-scripts` 경고). 빌드와 화면은 정상이에요. 문제가 생기면 `npm install-scripts approve <pkg>`로 허용해요.
- **에디터 자동완성**: VS Code는 호스트 파일을 보기 때문에, 호스트에서도 `npm install`, `uv sync`를 한 번 해 둬요. 노트북도 호스트 커널(`backend/.venv`)을 써요.
- **Windows 마운트**
  - `C:\xampp\...` 바인드 마운트는 느리고 변경 이벤트가 안 올 수 있어서 폴링을 켰어요. 백엔드 hot reload는 동작을 확인했어요.
  - 계속 느리면 Docker 공식 권장대로 저장소를 WSL2 파일시스템으로 옮겨요.
- **Docker 엔진 멈춤**: Docker Desktop 창은 떠 있는데 `docker` 명령이 응답하지 않거나 `500 Internal Server Error`가 나오면 Docker Desktop을 재시작해요(트레이 고래 아이콘 > Restart).
- **디스크**: 빌드를 반복하면 Docker vhdx가 커져요. 가끔 `docker system prune`을 해 주세요.

## fastapi-tistory와 다르게 하는 것
| tistory | 여기서는 | 이유 |
|---|---|---|
| Dockerfile 하나 (`--no-dev`인데 개발용으로 사용) | multi-stage `dev` / `prod` | 개발과 운영 이미지를 분리 |
| compose 하나 | `compose.yaml` + `override` + `prod` | 같은 파일로 개발과 배포 |
| `COPY ./app /app` | `COPY . .` | `app/`의 내용이 `/app`에 바로 들어가 `app.main:app`을 못 찾음 (마운트가 덮어써서 안 보일 뿐) |
| `COPY .env .env` | `env_file` (실행 시점) | 비밀값이 이미지에 박힘 |
| `.dockerignore` 없음 | 추가 | 빌드 컨텍스트에 DB 데이터, `.venv`까지 포함됨 |
| `pip install uv` | `COPY --from=ghcr.io/astral-sh/uv:0.10.6` | uv 버전 고정 (uv 공식 방식) |
| `venv_data` named volume | `/app/.venv` 익명 볼륨 + `-V` | named volume은 처음 한 번만 채워져서 옛 패키지가 남음 |
| entrypoint에서 uvicorn + Jupyter 동시 실행 | entrypoint는 역할별로 프로세스 하나 | 한쪽이 죽어도 알아채기 어려움 |
| 비밀번호가 compose에 직접 적힘 | `.env`의 `${DB_PASSWORD}` 참조 | 운영 값이 커밋되지 않게 |
| DB 데이터를 프로젝트 폴더에 바인드 | named volume `mysql_data` | Windows 마운트가 느리고 권한 문제가 생김 |
| `mongo:latest` | 버전 고정 | 메이저 버전이 바뀌어 깨지는 걸 막음 |
| `depends_on`만 | `healthcheck` + `service_healthy` | DB 준비 완료를 기다림 |
| `mysql_native_password` 옵션 | 사용 안 함 | MySQL 9에서 제거됨 |

## 적용 기록 (2026-10-21)
- 백업: `C:\xampp\htdocs\www\projects\claude-admin_backup_20261020` (옮기기 전 전체 복사본, git 기록 포함)
- 루트의 Next 파일 → `frontend/`, `backend/` 그대로. `git mv`로 옮겨서 `git log --follow`로 기록을 이어서 볼 수 있어요.
- `.gitignore`를 루트(공통) / `frontend/` / `backend/`로 나눔. `pyrightconfig.json` 제거. `.gitattributes` 추가
- 확인한 것
  - 로컬: 백엔드 pytest 42개, ruff, ty 통과. 프론트 `npm run build` (standalone 포함) 통과
  - 도커: 세 컨테이너 실행, health-check 200, `/admin` 200, fastapi 로그에서 Next의 `/api/v1/dashboard/*` 요청 확인
  - MySQL 9.7.2, `KST`, `utf8mb4_unicode_ci` 확인, 백엔드 hot reload 확인

## 남은 일
- [ ] 로컬 Node 24로 올리기 (`engines`, `.nvmrc`, `@types/node`)
- [ ] IPython `00-syspath.py`의 `PROJECT_ROOTS` 확인 (`...\claude-admin\backend` 그대로라 지금은 맞아요)
- [ ] `CLAUDE.md`를 루트(공통) / `frontend/` / `backend/`로 나눌지, `.claude/skills/fastapi`를 `backend/.claude/`로 옮길지
- [ ] 배포 이미지 실제 확인 (`docker compose -f compose.prod.yaml up -d --build`, `API_URL`·`FRONTEND_HOST` 값 필요)
- [ ] 배포 대상: 서버 한 대(compose.prod) / 클라우드(ECS, Cloud Run 등). 정해지면 HTTPS 앞단(Nginx/Caddy)과 CI 빌드를 계획
- [ ] Windows 마운트가 느리면 WSL2로 옮길지
- [ ] 나중에 백엔드 OpenAPI(`/api/openapi.json`)로 프론트 TS 타입을 자동 생성(`openapi-typescript`)해서 `dashboard.ts` ↔ `schemas/dashboard.py` 수동 동기화를 없애기
