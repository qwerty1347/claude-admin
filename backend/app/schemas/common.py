"""모든 API 가 공유하는 스키마: camelCase 베이스, 공통 응답 틀."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """파이썬에서는 snake_case, JSON 에서는 camelCase (FastAPI 는 응답을 by_alias 로 직렬화한다)."""

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)


# 성공·실패 판별은 HTTP 상태 코드로 한다. statusCode 는 같은 값을 본문에 한 번 더 적은 것.


class ApiResponse[T](CamelModel):
    """성공 응답: {"statusCode": 200, "code": "OK", "data": ...}"""

    status_code: int = 200
    code: str = "OK"
    data: T


class FieldError(CamelModel):
    field: str
    """오류 위치. 예: query.page, body.items.0.name"""
    message: str


class ApiError(CamelModel):
    """실패 응답: {"statusCode": 422, "code": "VALIDATION_ERROR", "message": ..., "errors": [...]}"""

    status_code: int
    code: str
    """프론트가 분기하는 기계용 값. 예: NOT_FOUND, ORDER_ALREADY_SHIPPED"""
    message: str
    """사람에게 보여주는 문구"""
    errors: list[FieldError] = []
    """필드별 오류. 없으면 빈 배열"""
