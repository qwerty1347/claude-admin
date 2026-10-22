"""실패 응답을 한 곳에서 ApiError 형식으로 만든다. 라우트에서는 try/except 대신 AppError 를 던진다.

예: raise AppError(status.HTTP_409_CONFLICT, "ORDER_ALREADY_SHIPPED", "이미 발송된 주문이에요")

팀 규칙: 업무 에러는 AppError 로 던진다 (code 를 지정할 수 있어서). HTTPException 은 문자열 detail 만 쓴다.
"""

import logging
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas import ApiError, FieldError

logger = logging.getLogger(__name__)

# HTTP 상태별 기본 code / message (AppError 에서 생략하거나 FastAPI 가 자동으로 낸 에러에 사용)
DEFAULT_ERRORS: dict[int, tuple[str, str]] = {
    status.HTTP_400_BAD_REQUEST: ("BAD_REQUEST", "잘못된 요청이에요"),
    status.HTTP_401_UNAUTHORIZED: ("UNAUTHORIZED", "로그인이 필요해요"),
    status.HTTP_403_FORBIDDEN: ("FORBIDDEN", "권한이 없어요"),
    status.HTTP_404_NOT_FOUND: ("NOT_FOUND", "찾을 수 없어요"),
    status.HTTP_405_METHOD_NOT_ALLOWED: (
        "METHOD_NOT_ALLOWED",
        "허용되지 않은 요청 방식이에요",
    ),
    status.HTTP_409_CONFLICT: ("CONFLICT", "요청이 현재 상태와 충돌해요"),
    status.HTTP_422_UNPROCESSABLE_CONTENT: (
        "VALIDATION_ERROR",
        "입력값을 확인해 주세요",
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: (
        "TOO_MANY_REQUESTS",
        "요청이 너무 많아요. 잠시 후 다시 시도해 주세요",
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: (
        "INTERNAL_ERROR",
        "일시적인 오류가 발생했어요",
    ),
}

FALLBACK_ERROR = ("ERROR", "요청을 처리하지 못했어요")


def error_responses(*status_codes: int) -> dict[int | str, dict[str, Any]]:
    """/docs 에 실패 응답(ApiError)을 표시할 상태만 골라 붙인다. 실제로 낼 수 있는 상태만 넣는다.

    예: @router.get("/{order_id}", responses=error_responses(status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_CONTENT))
    파라미터가 있는 라우트는 FastAPI 가 기본 형식의 422 를 자동으로 붙이므로 422 를 넣어 ApiError 로 덮어쓴다.
    """
    return {
        code: {
            "model": ApiError,
            "description": DEFAULT_ERRORS.get(code, FALLBACK_ERROR)[1],
        }
        for code in status_codes
    }


def _http_exception_message(status_code: int, detail: object) -> str:
    """HTTPException 의 detail 을 사용자 메시지로 쓸지 정한다.

    - 직접 쓴 문자열 detail("주문을 찾을 수 없어요")은 그대로 쓴다.
    - HTTP 기본 문구("Not Found" 등, 없는 경로처럼 Starlette 이 자동으로 낸 에러)와
      문자열이 아닌 detail(dict 등)은 한글 기본 문구로 바꾼다.
    """
    default = DEFAULT_ERRORS.get(status_code, FALLBACK_ERROR)[1]
    if not isinstance(detail, str) or not detail:
        return default
    try:
        standard_phrase = HTTPStatus(status_code).phrase
    except ValueError:
        standard_phrase = None
    return default if detail == standard_phrase else detail


class AppError(Exception):
    """업무 에러. code·message 를 생략하면 상태별 기본값을 쓴다."""

    def __init__(
        self,
        status_code: int,
        code: str | None = None,
        message: str | None = None,
        errors: list[FieldError] | None = None,
    ) -> None:
        default_code, default_message = DEFAULT_ERRORS.get(status_code, FALLBACK_ERROR)
        self.status_code = status_code
        self.code = code or default_code
        self.message = message or default_message
        self.errors = errors or []
        super().__init__(self.message)


def _error_response(
    status_code: int,
    code: str,
    message: str,
    errors: list[FieldError] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body = ApiError(
        status_code=status_code, code=code, message=message, errors=errors or []
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json", by_alias=True),
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, exc.errors)

    @app.exception_handler(RequestValidationError)
    def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        code, message = DEFAULT_ERRORS[status.HTTP_422_UNPROCESSABLE_CONTENT]
        errors = [
            FieldError(field=".".join(str(p) for p in e["loc"]), message=e["msg"])
            for e in exc.errors()
        ]
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT, code, message, errors
        )

    @app.exception_handler(StarletteHTTPException)
    def handle_http_exception(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        # 없는 경로(404), 허용 안 된 메서드(405), 라우트에서 던진 HTTPException 등
        code = DEFAULT_ERRORS.get(exc.status_code, FALLBACK_ERROR)[0]
        message = _http_exception_message(exc.status_code, exc.detail)
        return _error_response(exc.status_code, code, message, headers=exc.headers)

    @app.exception_handler(Exception)
    def handle_unexpected_error(request: Request, _exc: Exception) -> JSONResponse:
        # 내부 내용은 본문에 넣지 않고 로그에만 남긴다
        logger.exception("Unhandled error: %s %s", request.method, request.url.path)
        code, message = DEFAULT_ERRORS[status.HTTP_500_INTERNAL_SERVER_ERROR]
        return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code, message)
