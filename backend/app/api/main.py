from fastapi import APIRouter

from app.api import v1
from app.core.config import settings

# 버전은 설정이 아니라 app/api/v1/, v2/ ... 패키지의 라우터 prefix로 나눈다.
# 새 버전이 생기면 app/api/vN/을 만들고 여기에 include_router 한 줄을 추가한다.
api_router = APIRouter(prefix=settings.API_PREFIX)
api_router.include_router(v1.router)
