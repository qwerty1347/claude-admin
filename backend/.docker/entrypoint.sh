#!/bin/sh
set -e

# SERVICE_TYPE: 컨테이너 역할 (compose.yaml 의 environment 로 지정)
# ENVIRONMENT : local 이면 개발(fastapi dev, hot reload), 그 외(production)는 fastapi run
case "$SERVICE_TYPE" in
    app)
        if [ "$ENVIRONMENT" = "local" ]; then
            exec uv run fastapi dev --host 0.0.0.0 --port 8000
        else
            exec fastapi run --host 0.0.0.0 --port 8000
        fi
        ;;
    # worker)   # 백그라운드 작업이 생기면 compose 에 SERVICE_TYPE: worker 서비스를 추가
    #     exec uv run arq app.worker.WorkerSettings
    #     ;;
    *)
        echo "ERROR: SERVICE_TYPE is not set or invalid: '$SERVICE_TYPE'"
        echo "Valid values: app"
        exit 1
        ;;
esac
