# 모노레포 정리 + 도커 개발·배포 환경 계획 (2026-10-20)

## Context
지금은 한 저장소(`claude-admin`)의 루트에 Next가 있고 FastAPI는 `backend/`에 있어요. 둘 다 로컬에서 각각 띄워요(3001, 9101).
- 다른 PC에서 작업하려면 Node, uv, (나중에) DB를 다시 설치해야 해요.
- 원하는 모습
  - **git 저장소는 하나**: push하는 곳이 한 곳 (GitHub `qwerty1347/claude-admin` 그대로)
  - **로컬은 프로젝트별로**: `nextjs/`와 `fastapi/`가 각자 독립 프로젝트예요. 각자 VS Code 창, 각자 `compose.yaml`이 있어서 그 폴더에서 `docker compose up` 하면 그 프로젝트만 떠요.
- 그래서 **모노레포(저장소 하나, 하위 폴더 둘) + 폴더별 compose** 구조로 가요.
- 개발용과 배포용은 처음부터 나눠요. 실무 표준 방식(compose base + override + prod, Dockerfile multi-stage, 환경별 env)을 써요.

## 구조
```
claude-admin\                      git 저장소 1개 (push 한 곳)
├─ compose.yaml                    전체 실행 (개발): 두 프로젝트를 include, 프로젝트 이름 claude-admin
├─ compose.prod.yaml               전체 실행 (배포)
├─ CLAUDE.md                       공통 규칙 (커밋, 문서, 두 프로젝트 관계)
├─ README.md  .gitignore           .gitignore 는 공통(.env 등)만
├─ docs\                           0~3 계획 문서
├─ nextjs\                         ← 로컬 프로젝트 1 (VS Code 창 1)
│  ├─ compose.yaml                 공통
│  ├─ compose.override.yaml        개발 (docker compose up 이 자동으로 합침)
│  ├─ compose.prod.yaml            배포
│  ├─ .docker\Dockerfile           multi-stage (dev / build / prod)
│  ├─ .dockerignore  .gitignore
│  ├─ .env.example (커밋)  .env.local (커밋 X)
│  ├─ .claude\settings.json        npm 명령 허용
│  ├─ CLAUDE.md                    프론트 규칙
│  └─ src\ public\ package.json package-lock.json next.config.ts tsconfig.json
│     eslint.config.mjs postcss.config.mjs AGENTS.md
└─ fastapi\                        ← 로컬 프로젝트 2 (VS Code 창 2, 지금 backend\ 이름만 변경)
   ├─ compose.yaml  compose.override.yaml  compose.prod.yaml   fastapi + mysql
   ├─ .docker\Dockerfile           multi-stage (dev / prod)
   ├─ .dockerignore  .gitignore
   ├─ .env.example (커밋)  .env (커밋 X)
   ├─ .claude\settings.json  .claude\skills\fastapi\
   ├─ CLAUDE.md                    백엔드 규칙
   └─ app\ tests\ notebooks\ pyproject.toml uv.lock .python-version
```
- 하위 폴더만 열어도 VS Code가 상위 `.git`을 찾아서 Source Control이 그대로 동작해요. 커밋과 push도 그 창에서 하면 돼요(저장소는 하나).
- `fastapi\`를 루트로 열면 Pylance가 `.venv`를 바로 찾아요. 그래서 루트 `pyrightconfig.json`은 지워요.
- Claude Code는 실행한 폴더부터 상위 폴더까지 `CLAUDE.md`를 읽어요. 하위 폴더에서 작업해도 루트의 공통 규칙이 같이 적용돼요.
- compose 파일 이름은 Compose 공식 기본 이름(`compose.yaml`)이에요. `docker-compose.yml`도 읽히지만 예전 이름이에요.

## 전체 실행 (루트 compose, include)
평소에는 루트에서 한 번에 띄워요. Docker Desktop에서는 `claude-admin` 묶음 하나로 보여요.
```
Docker Desktop > Containers
▼ claude-admin                  ← compose 프로젝트 1개
    claude_admin-nextjs         ← 컨테이너
    claude_admin-fastapi
    claude_admin-mysql
```

### compose.yaml (루트, 개발)
```yaml
name: claude-admin

include:
  - path:
      - fastapi/compose.yaml
      - fastapi/compose.override.yaml
  - path:
      - nextjs/compose.yaml
      - nextjs/compose.override.yaml
```

### compose.prod.yaml (루트, 배포)
```yaml
name: claude-admin

include:
  - path:
      - fastapi/compose.yaml
      - fastapi/compose.prod.yaml
  - path:
      - nextjs/compose.yaml
      - nextjs/compose.prod.yaml
```
- `include`는 Compose 공식 기능이에요(2.20 이상, 이 PC는 2.34).
  - 포함된 파일의 상대 경로(`./`, `.docker/Dockerfile`)와 `.env`는 그 파일이 있는 폴더 기준으로 읽혀요. 그래서 폴더별 compose를 고치지 않아도 돼요.
- `include`는 지정한 파일만 읽어요. 그래서 개발용(`override`)과 배포용(`prod`)을 위처럼 짝으로 적어요.
- 각 폴더에서 따로 띄우는 것도 돼요(`fastapi/`에서 `docker compose up -d`). 이때는 Docker Desktop에 `fastapi` 묶음으로 따로 보여요.
  - 루트 실행과 폴더 실행은 동시에 쓰지 않아요. `container_name`이 같아서 이름 충돌 에러가 나요. 바꿀 때는 먼저 `down` 해요.
- 한 프로젝트로 묶여도 nextjs의 `API_URL`은 `host.docker.internal:9101` 그대로 써요. 폴더 단독 실행과 로컬 방식에서도 같은 주소로 동작하게 하려고요.

## git 사용
- **push는 한 번**이에요. 두 폴더를 같이 고쳤으면 커밋 하나로 묶을 수도 있어요.
- **한 프로젝트만 받기**: `sparse-checkout`
  ```bash
  git clone --filter=blob:none --sparse https://github.com/qwerty1347/claude-admin.git
  cd claude-admin
  git sparse-checkout set fastapi      # 작업 폴더에는 fastapi/ (+ 루트 파일)만
  git sparse-checkout add nextjs       # 나중에 추가
  git sparse-checkout disable          # 전부 받기
  ```
- **한 프로젝트 기록만 보기**: `git log -- fastapi/`
- **커밋 메시지**: 어느 쪽 변경인지 접두어를 붙여요. 예: `[fastapi] 주문 API 추가`, `[nextjs] KPI 티커`
- **배포 자동화(나중에)**: GitHub Actions에서 `paths: ["fastapi/**"]`처럼 경로 필터를 걸어, 바뀐 프로젝트만 빌드하고 배포해요.

## 개발 / 배포 차이
| | 개발 (`compose.yaml` + `compose.override.yaml`) | 배포 (`compose.yaml` + `compose.prod.yaml`) |
|---|---|---|
| Dockerfile stage | `dev` | `prod` |
| 실행 | `next dev`, `fastapi dev` (hot reload) | `node server.js`, `fastapi run` (빌드 결과) |
| 소스 | 바인드 마운트 (저장하면 바로 반영) | 이미지에 포함 (마운트 없음) |
| 패키지 | dev 포함 (eslint, pytest, ruff, ty) | 운영에 필요한 것만 |
| 실행 계정 | root (기본) | 일반 사용자 |
| 재시작 | 없음 | `restart: unless-stopped` |
| DB 포트 | 호스트에 공개 (3307, DB 툴 접속용) | 공개 안 함 |
| 비밀값 | `.env` (`.env.example` 복사) | 서버의 `.env` 또는 배포 도구 Secrets |

## 포트와 연결
| 프로젝트 | 서비스 | container_name | 호스트 → 컨테이너 |
|---|---|---|---|
| nextjs | `nextjs` | `claude_admin-nextjs` | 3001 → 3001 |
| fastapi | `fastapi` | `claude_admin-fastapi` | 9101 → 8000 |
| fastapi | `mysql` | `claude_admin-mysql` | 3307 → 3306 (개발만. 호스트 3306은 XAMPP MySQL 자리) |

- **nextjs → fastapi**: compose가 서로 다른 프로젝트라서 서비스 이름으로는 못 불러요. 호스트에 열린 백엔드 포트로 불러요.
  - 개발: `API_URL=http://host.docker.internal:9101`
    - Docker Desktop(Windows, Mac)은 이 주소를 기본으로 지원해요. Linux에서도 되도록 `extra_hosts: host.docker.internal:host-gateway`를 넣어요.
    - fastapi를 도커로 띄웠든 로컬(`uv run fastapi dev --port 9101`)로 띄웠든 같은 주소라서 섞어 써도 돼요.
  - 배포: 서버 환경변수로 실제 API 주소를 넣어요. 예: `API_URL=https://api.example.com`
- **fastapi → mysql**: 같은 compose라서 서비스 이름 `mysql:3306`으로 불러요.
- **env 규칙**
  - 각 프로젝트의 env 파일(`nextjs/.env.local`, `fastapi/.env`)에는 로컬 방식 값을 넣어요(`127.0.0.1:9101`, `127.0.0.1:3307`).
  - 도커에서는 compose의 `environment`가 그 값을 덮어써요.
  - Next와 pydantic-settings 둘 다 이미 있는 환경변수를 env 파일로 덮지 않아요. 그래서 파일을 고치지 않아도 두 방식을 다 쓸 수 있어요.

## nextjs/

### .docker/Dockerfile
Next 공식 Docker 예시(standalone 출력) 구조예요.
```dockerfile
FROM node:24-slim AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# 개발
FROM deps AS dev
COPY . .
CMD ["npm", "run", "dev"]

# 빌드
FROM deps AS build
COPY . .
RUN npm run build

# 배포: 빌드 결과만, 일반 사용자로 실행
FROM base AS prod
ENV NODE_ENV=production PORT=3001 HOSTNAME=0.0.0.0
COPY --from=build /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
CMD ["node", "server.js"]
```
- `next.config.ts`에 `output: "standalone"`을 추가해요. 배포 이미지에 필요한 파일만 담겨요.

### compose.yaml (공통)
```yaml
services:
  nextjs:
    build:
      context: .
      dockerfile: .docker/Dockerfile
    container_name: claude_admin-nextjs
```

### compose.override.yaml (개발)
```yaml
services:
  nextjs:
    build:
      target: dev
    ports:
      - "3001:3001"
    volumes:
      - ./:/app
      - /app/node_modules              # 컨테이너(Linux)용 패키지. 호스트 것으로 덮이지 않게
      - /app/.next
    environment:
      API_URL: http://host.docker.internal:9101
      WATCHPACK_POLLING: "true"        # Windows 마운트에서 변경 감지
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### compose.prod.yaml (배포)
```yaml
services:
  nextjs:
    build:
      target: prod
    restart: unless-stopped
    ports:
      - "3001:3001"                    # 앞단 Nginx/Caddy(HTTPS)가 여기로 전달
    environment:
      API_URL: ${API_URL}              # 서버 환경변수. 예: https://api.example.com
```

### .env.example (커밋)
```dotenv
# .env.local 로 복사해서 사용 (로컬 방식용. 도커에서는 compose 값이 우선)
# localhost 대신 127.0.0.1: Node fetch 가 localhost 를 IPv6(::1)로 풀면 연결되지 않는다
API_URL=http://127.0.0.1:9101
```

### .dockerignore
```
node_modules
.next
.env*
.playwright-mcp
```

## fastapi/

### .docker/Dockerfile
```dockerfile
FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.10.6 /uv /uvx /bin/
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY --chmod=755 .docker/entrypoint.sh /entrypoint.sh   # 소스 마운트(/app) 바깥
ENTRYPOINT ["/entrypoint.sh"]

# 개발: dev 의존성 포함, hot reload
FROM base AS dev
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-install-project
COPY . .

# 배포: 운영 의존성만, 일반 사용자로 실행
FROM base AS prod
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY . .
RUN uv sync --locked --no-dev
RUN useradd --system --no-create-home app
USER app
```

### .docker/entrypoint.sh (fastapi-tistory 방식)
- 실행 명령은 `SERVICE_TYPE`(역할)과 `ENVIRONMENT`(local / production)로 골라요.
  - `app` + `local`: `uv run fastapi dev` (hot reload)
  - `app` + 그 외: `fastapi run`
  - `worker`는 주석으로 자리만 잡아 뒀어요.
- compose의 `SERVICE_TYPE: app`, `.env`의 `ENVIRONMENT=local`, `compose.prod.yaml`의 `ENVIRONMENT: production`이 값을 정해요.
- 줄바꿈은 루트 `.gitattributes`(`*.sh text eol=lf`)로 LF를 고정해요. CRLF가 되면 Linux에서 스크립트가 실행되지 않아요.
- `/app` 바깥(`/entrypoint.sh`)에 복사해서 소스 마운트가 덮어쓰지 않아요. 그래서 이 파일을 고친 뒤에는 `--build`로 다시 빌드해야 해요.
- 의존성 파일을 코드보다 먼저 복사해요. 코드만 바뀐 빌드에서는 설치 단계가 캐시돼요.
- `--host 0.0.0.0`이 꼭 필요해요. 기본값이 127.0.0.1이라서, 빠뜨리면 컨테이너 밖에서 접속이 안 돼요.

### compose.yaml (공통)
```yaml
services:
  fastapi:
    build:
      context: .
      dockerfile: .docker/Dockerfile
    container_name: claude_admin-fastapi
    env_file: .env
    environment:
      DATABASE_URL: mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}?charset=utf8mb4
    depends_on:
      mysql:
        condition: service_healthy

  mysql:
    image: mysql:9.7
    container_name: claude_admin-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      TZ: Asia/Seoul                   # DB 시간대 = 한국 시간 (NOW(), CURRENT_TIMESTAMP)
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -u root -p$$MYSQL_ROOT_PASSWORD --silent"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 20s                # 첫 실행은 초기화로 오래 걸림

volumes:
  mysql_data:
```
- `${DB_USER}` 같은 값은 compose가 같은 폴더의 `.env`에서 읽어요.

### compose.override.yaml (개발)
```yaml
services:
  fastapi:
    build:
      target: dev
    ports:
      - "9101:8000"
    volumes:
      - ./:/app
      - /app/.venv                     # 컨테이너(Linux)용 가상환경. 호스트 .venv 로 덮이지 않게
    environment:
      WATCHFILES_FORCE_POLLING: "true"

  mysql:
    ports:
      - "3307:3306"                    # DB 툴, 로컬 방식 백엔드 접속용
```

### compose.prod.yaml (배포)
```yaml
services:
  fastapi:
    build:
      target: prod
    restart: unless-stopped
    ports:
      - "9101:8000"                    # 앞단 Nginx/Caddy(HTTPS)가 여기로 전달
    environment:
      ENVIRONMENT: production
      FRONTEND_HOST: ${FRONTEND_HOST}  # 예: https://admin.example.com

  mysql:
    restart: unless-stopped
    # ports 없음: DB는 외부에 열지 않음
```

### .env.example (커밋)
```dotenv
# .env 로 복사해서 사용. 아래 DB 값은 개발 전용 (운영 서버에서는 반드시 다른 값)
ENVIRONMENT=local
FRONTEND_HOST=http://localhost:3001
TIMEZONE=Asia/Seoul

# compose 가 mysql 컨테이너를 만들 때 쓰는 값
DB_NAME=fastapi
DB_USER=admin
DB_PASSWORD=admin
DB_ROOT_PASSWORD=root

# 로컬 방식(uv run fastapi dev)용. 도커에서는 compose 가 mysql:3306 으로 덮어씀
DATABASE_URL=mysql+aiomysql://admin:admin@127.0.0.1:3307/fastapi?charset=utf8mb4
```
- 개발 DB 접속 정보: DB `fastapi`, 사용자 `admin` / `admin`, root `root`
  - 호스트(DB 툴)에서는 `127.0.0.1:3307`, 컨테이너 안에서는 `mysql:3306`으로 접속해요.
- 개발 값은 `.env.example`에 두고 커밋해도 돼요. 운영 값은 서버의 `.env`나 배포 도구(GitHub Actions Secrets 등)로 넣어요.

### .dockerignore
```
.venv
__pycache__
.ruff_cache
.pytest_cache
.env
notebooks
```

## 사용법
| 하고 싶은 것 | 위치 | 명령 |
|---|---|---|
| 전부 띄우기 (개발) | 루트 | `docker compose up -d` → Docker Desktop에 `claude-admin` 하나 |
| 전부 끄기 | 루트 | `docker compose down` |
| 일부만 (루트에서) | 루트 | `docker compose up -d fastapi mysql` |
| 한 프로젝트만 띄우기 | 각 프로젝트 폴더 | `docker compose up -d` (루트 실행과 동시에 쓰지 않음) |
| DB만 띄우고 백엔드는 로컬 | `fastapi/` | `docker compose up -d mysql` → `uv run fastapi dev --port 9101` |
| 로그 | 각 프로젝트 | `docker compose logs -f fastapi` / `nextjs` |
| 테스트·린트 | `fastapi/` | `docker compose exec fastapi uv run pytest -q` (ruff, ty도 같은 식) |
| 린트 | `nextjs/` | `docker compose exec nextjs npm run lint` |
| 패키지 추가 | `fastapi/` | `docker compose exec fastapi uv add <pkg>` → `docker compose up -d --build -V fastapi` |
| 패키지 추가 | `nextjs/` | `docker compose exec nextjs npm install <pkg>` → `docker compose up -d --build -V nextjs` |
| 끄기 | 각 프로젝트 | `docker compose down` (DB 데이터 유지, `-v`를 붙이면 삭제) |
| 배포 이미지로 띄우기 | 루트 | `docker compose -f compose.prod.yaml up -d --build` |
| 배포 이미지로 띄우기 (한 프로젝트) | 각 프로젝트 | `docker compose -f compose.yaml -f compose.prod.yaml up -d --build` |

- `-V`: 익명 볼륨(`node_modules`, `.venv`)을 새로 만들어요. 안 붙이면 패키지를 바꾸고 다시 빌드해도 옛 볼륨이 남아요.
- 로컬 방식: `cd nextjs && npm run dev`, `cd fastapi && uv run fastapi dev --port 9101`

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
  - 확인: `SELECT @@system_time_zone, @@time_zone, NOW();` → `KST`, `SYSTEM`, 한국 시간
- **인증**
  - 기본 `caching_sha2_password`를 써요. `mysql_native_password` 옵션은 MySQL 9에서 없어져서, 넣으면 컨테이너가 뜨지 않아요.
  - aiomysql과 PyMySQL은 이 인증 방식에 `cryptography`가 필요해요.
- **초기화**
  - 문자셋, `MYSQL_DATABASE`, `MYSQL_USER`는 볼륨이 비어 있을 때 기준이에요.
  - 값을 바꿨다면 `docker compose down -v`로 볼륨을 지우고 다시 띄워요. 데이터도 지워져요.
  - 확인: `SHOW VARIABLES LIKE 'character_set_server';`, `SHOW VARIABLES LIKE 'collation_server';`
- **운영**: 서버 한 대라면 위 compose로 띄우고 정기 백업(`mysqldump`)을 해요. 규모가 커지면 관리형 DB(AWS RDS 등)로 옮기고 `DATABASE_URL`만 바꿔요.
- **ORM: SQLAlchemy 2, 비동기 + 동기 둘 다** (자세한 규칙은 `2 BACKEND-PLAN.md`의 "DB 접근")
  - 비동기 `mysql+aiomysql`은 API 라우트 기본이에요. 동기 `mysql+pymysql`은 Alembic, 시드, 스크립트, 노트북, 동기 라우트에서 써요.
  - 접속 정보는 `DATABASE_URL` 하나(aiomysql)만 두고, 동기 URL은 드라이버 이름만 바꿔서 만들어요. 그래서 compose와 env 파일은 지금 그대로예요.
  - `uv add "sqlalchemy[asyncio]" aiomysql pymysql cryptography alembic`

## 폴더 옮기기 (git 기록 유지)
`git mv`로 옮기면 파일 기록이 이어져요(`git log --follow`). 새 저장소나 원격 주소 변경은 필요 없어요.
```bash
git mv backend fastapi
mkdir nextjs
git mv src public package.json package-lock.json next.config.ts tsconfig.json \
       eslint.config.mjs postcss.config.mjs AGENTS.md nextjs/
git mv .env.example nextjs/.env.example
git rm pyrightconfig.json
```
- 커밋되지 않은 것은 직접 옮기거나 다시 만들어요.
  - `.env.local` → `nextjs/.env.local`
  - `backend/notebooks/`는 `git mv backend` 때 폴더째 같이 옮겨져요.
  - `node_modules`, `.next`, `tsconfig.tsbuildinfo`, `next-env.d.ts`, `fastapi/.venv`는 지우고 각 폴더에서 `npm ci`, `uv sync`로 다시 만들어요. `.venv`에는 옛 경로가 남아 있어서 다시 만드는 게 안전해요.
- 같이 고칠 것
  | 파일 | 변경 |
  |---|---|
  | `.gitignore` | 루트는 공통(`.env` 등)만. Next 규칙은 `nextjs/.gitignore`, Python 규칙은 `fastapi/.gitignore`로 나눔 (지금 `/node_modules`처럼 루트 기준 경로라서) |
  | `CLAUDE.md` | 루트: 공통 규칙과 두 프로젝트 관계, 타입 동기화(`nextjs/src/types/dashboard.ts` ↔ `fastapi/app/schemas/dashboard.py`). `nextjs/CLAUDE.md`, `fastapi/CLAUDE.md`: 각 명령과 규칙 |
  | `.claude/` | `skills/fastapi` → `fastapi/.claude/skills/`. `settings.json`은 폴더별로 (npm / uv 명령 허용) |
  | IPython `00-syspath.py` | `PROJECT_ROOTS`의 `...\claude-admin\backend` → `...\claude-admin\fastapi` |
  | docs, README | `backend/` 경로 표기를 `fastapi/`로 |
- 나중에는 백엔드 OpenAPI(`/api/openapi.json`)로 `nextjs`의 TS 타입을 자동 생성(`openapi-typescript`)해서 수동 동기화를 없애요.

## 주의할 점
- **Node 버전**
  - Node 20은 2026-04-30에 지원이 끝났어요(EOL). 이미지는 현재 LTS인 `node:24`를 써요.
  - 로컬 Node도 24로 올리고(지금 20.15), `nextjs/package.json`에 `"engines": { "node": ">=24" }`와 `nextjs/.nvmrc`(`24`)를 둬요. `@types/node`도 `^24`로 맞춰요.
- **에디터 자동완성**: VS Code는 호스트 파일을 보기 때문에, 호스트에서도 `npm ci`, `uv sync`를 한 번 해 둬요. 노트북도 호스트 커널(`fastapi/.venv`)을 써요.
- **Windows 마운트**
  - `C:\xampp\...` 바인드 마운트는 느리고 변경 이벤트가 안 올 수 있어서 폴링을 켜요.
  - Next 16 dev는 Turbopack이 기본이에요. 폴링 설정으로 hot reload가 되는지 단계 4에서 확인해요.
  - 계속 느리면 Docker 공식 권장대로 저장소를 WSL2 파일시스템으로 옮겨요.
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
| 비밀번호가 compose에 직접 적힘 | `.env`의 `${DB_PASSWORD}` 참조 | 운영 값이 커밋되지 않게 |
| DB 데이터를 프로젝트 폴더에 바인드 | named volume `mysql_data` | Windows 마운트가 느리고 권한 문제가 생김 |
| `mongo:latest` | 버전 고정 | 메이저 버전이 바뀌어 깨지는 걸 막음 |
| 한 컨테이너에 uvicorn + Jupyter | 컨테이너당 프로세스 하나 | 한쪽이 죽어도 알아채기 어려움 |
| `depends_on`만 | `healthcheck` + `service_healthy` | DB 준비 완료를 기다림 |
| `mysql_native_password` 옵션 | 사용 안 함 | MySQL 9에서 제거됨 |

## 단계
1. **폴더 옮기기**: `git mv`로 `fastapi/`, `nextjs/` 구성, `.gitignore`·IPython 경로 수정
   - 로컬 방식으로 지금과 똑같이 동작하는지 확인 (`npm run build`, `uv run pytest -q`, `/admin` 화면) → 커밋
2. **정리**: `CLAUDE.md` 3개, `.claude/` 나누기, docs·README 경로, Node 24 맞추기 → 커밋
3. **fastapi 도커**: `fastapi/`에 Dockerfile, `compose*.yaml`, `.env.example`, `.dockerignore`
   - `docker compose up -d` → health-check, pytest, ruff, ty 확인 → 커밋
4. **nextjs 도커**: `nextjs/`에 Dockerfile, `compose*.yaml`, `.dockerignore`, `output: "standalone"`
   - `/admin`에서 실제 API 데이터와 hot reload 확인 → 커밋
5. **배포 이미지 확인**: 각 프로젝트에서 `-f compose.yaml -f compose.prod.yaml up -d --build` (nextjs는 `API_URL=http://host.docker.internal:9101`로 테스트)
6. **루트 compose**: `compose.yaml`, `compose.prod.yaml`(include) 추가 → 루트에서 `up -d`, Docker Desktop에 `claude-admin` 하나로 보이는지 확인 → 커밋
7. 각 `CLAUDE.md`에 도커 명령 추가 → 커밋

## 확인 방법
- `fastapi/`에서 `docker compose ps`: fastapi는 running, mysql은 `healthy`
- `curl http://localhost:9101/api/v1/utils/health-check/` → `{"statusCode":200,"code":"OK","data":true}`
- `nextjs/`에서 띄운 뒤 `http://localhost:3001/admin`이 떠요. fastapi를 끄고 새로고침하면 error.tsx 화면이 나와요. 실제 API를 쓰고 있다는 증거예요.
- DB 툴로 `127.0.0.1:3307`, `admin` / `admin`, DB `fastapi`에 접속돼요.
- `SELECT @@system_time_zone, NOW();`이 한국 시간이고, `collation_server`는 `utf8mb4_unicode_ci`예요.
- 파일을 저장하면 몇 초 안에 화면과 API 응답이 바뀌어요.
- prod 이미지에서 `docker compose exec fastapi whoami` → `app` (root 아님)
- `git sparse-checkout set fastapi`로 받은 clone에 `nextjs/`가 없어요.

## 결정할 것
- [x] 구조: 모노레포 (git 1개), 로컬 프로젝트 `nextjs/`, `fastapi/` 각자 compose
- [x] 전체 실행: 루트 compose(`name: claude-admin` + include)로 compose 프로젝트 하나에 컨테이너 3개
- [x] DB: MySQL 9.7 (LTS), Asia/Seoul, `utf8mb4_unicode_ci`
- [x] DB 접근: SQLAlchemy 2. 비동기(`AsyncSession` + `aiomysql`)와 동기(`Session` + `pymysql`) 둘 다
- [ ] 배포 대상: 서버 한 대(compose.prod) / 클라우드(ECS, Cloud Run 등). 정해지면 HTTPS 앞단(Nginx/Caddy)과 CI 빌드를 계획
- [ ] Windows 마운트가 느리면 WSL2로 옮길지
