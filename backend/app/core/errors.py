"""실패 응답을 한 곳에서 ApiError 형식으로 만든다. 라우트에서는 try/except 대신 AppError 를 던진다.

예: raise AppError(409, "ORDER_ALREADY_SHIPPED", "이미 발송된 주문이에요")
"""

import logging
from collections.abc import Mapping

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas import ApiError, FieldError

logger = logging.getLogger(__name__)

# HTTP 상태별 기본 code / message (AppError 에서 생략하거나 FastAPI 가 자동으로 낸 에러에 사용)
DEFAULT_ERRORS: dict[int, tuple[str, str]] = {
    400: ("BAD_REQUEST", "잘못된 요청이에요"),
    401: ("UNAUTHORIZED", "로그인이 필요해요"),
    403: ("FORBIDDEN", "권한이 없어요"),
    404: ("NOT_FOUND", "찾을 수 없어요"),
    405: ("METHOD_NOT_ALLOWED", "허용되지 않은 요청 방식이에요"),
    409: ("CONFLICT", "요청이 현재 상태와 충돌해요"),
    422: ("VALIDATION_ERROR", "입력값을 확인해 주세요"),
    429: ("TOO_MANY_REQUESTS", "요청이 너무 많아요. 잠시 후 다시 시도해 주세요"),
    500: ("INTERNAL_ERROR", "일시적인 오류가 발생했어요"),
}


class AppError(Exception):
    """업무 에러. code·message 를 생략하면 상태별 기본값을 쓴다."""

    def __init__(
        self,
        status_code: int,
        code: str | None = None,
        message: str | None = None,
        errors: list[FieldError] | None = None,
    ) -> None:
        default_code, default_message = DEFAULT_ERRORS.get(
            status_code, ("ERROR", "요청을 처리하지 못했어요")
        )
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
        code, message = DEFAULT_ERRORS[422]
        errors = [
            FieldError(field=".".join(str(p) for p in e["loc"]), message=e["msg"])
            for e in exc.errors()
        ]
        return _error_response(422, code, message, errors)

    @app.exception_handler(StarletteHTTPException)
    def handle_http_exception(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        # 없는 경로(404), 허용 안 된 메서드(405), 라우트에서 던진 HTTPException 등
        code, message = DEFAULT_ERRORS.get(exc.status_code, ("ERROR", str(exc.detail)))
        return _error_response(exc.status_code, code, message, headers=exc.headers)

    @app.exception_handler(Exception)
    def handle_unexpected_error(request: Request, _exc: Exception) -> JSONResponse:
        # 내부 내용은 본문에 넣지 않고 로그에만 남긴다
        logger.exception("Unhandled error: %s %s", request.method, request.url.path)
        code, message = DEFAULT_ERRORS[500]
        return _error_response(500, code, message)
