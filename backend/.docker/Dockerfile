# stage: dev / prod. 실행 명령은 .docker/entrypoint.sh 가 SERVICE_TYPE, ENVIRONMENT 로 고른다
FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.10.6 /uv /uvx /bin/
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
# 소스 마운트(/app) 바깥에 두어서 마운트가 덮어쓰지 않게 한다
COPY --chmod=755 .docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# 개발: dev 의존성 포함. compose.override.yaml 에서 소스를 마운트하고 hot reload
# 의존성 파일을 코드보다 먼저 복사해서, 코드만 바뀐 빌드는 설치 단계를 캐시로 건너뛴다
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
