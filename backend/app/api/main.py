from fastapi import APIRouter

from app.api import v1
from app.core.config import settings
from app.schemas import ApiError

# 버전은 설정이 아니라 app/api/v1/, v2/ ... 패키지의 라우터 prefix로 나눈다.
# 새 버전이 생기면 app/api/vN/을 만들고 여기에 include_router 한 줄을 추가한다.
api_router = APIRouter(
    prefix=settings.API_PREFIX,
    # /docs 에 실패 응답 형식 표시 (실제 변환은 app/core/errors.py 의 예외 핸들러)
    responses={
        404: {"model": ApiError, "description": "찾을 수 없음"},
        422: {"model": ApiError, "description": "입력값 검증 실패"},
        500: {"model": ApiError, "description": "서버 오류"},
    },
)
api_router.include_router(v1.router)
