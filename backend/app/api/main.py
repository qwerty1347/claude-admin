from fastapi import APIRouter

from app.api import v1
from app.core.config import settings
from app.core.errors import error_responses

# 버전은 설정이 아니라 app/api/v1/, v2/ ... 패키지의 라우터 prefix로 나눈다.
# 새 버전이 생기면 app/api/vN/을 만들고 여기에 include_router 한 줄을 추가한다.
api_router = APIRouter(
    prefix=settings.API_PREFIX,
    # /docs 에 실패 응답 형식 표시 (실제 변환은 app/core/errors.py 의 예외 핸들러).
    # 공통으로는 어느 라우트든 낼 수 있는 500만. 404·422 등은 실제로 내는 라우트에서 error_responses() 로 붙인다.
    responses=error_responses(500),
)
api_router.include_router(v1.router)
