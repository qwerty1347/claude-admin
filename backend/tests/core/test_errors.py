"""예외 핸들러가 모든 실패를 ApiError 형식으로 바꾸는지 확인한다 (테스트 전용 앱 사용)."""

from typing import Annotated

import pytest
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

from app.core.errors import AppError, register_exception_handlers
from app.main import app as main_app


def build_app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/conflict")
    def conflict() -> None:
        raise AppError(409, "ORDER_ALREADY_SHIPPED", "이미 발송된 주문이에요")

    @test_app.get("/default-message")
    def default_message() -> None:
        raise AppError(404)

    @test_app.get("/items")
    def items(page: Annotated[int, Query(ge=1)]) -> int:
        return page

    @test_app.get("/boom")
    def boom() -> None:
        raise RuntimeError("secret internal detail")

    return test_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    # 500 을 응답으로 받기 위해 서버 예외를 테스트로 다시 던지지 않게 한다
    return TestClient(build_app(), raise_server_exceptions=False)


def test_app_error(client: TestClient) -> None:
    r = client.get("/conflict")
    assert r.status_code == 409
    assert r.json() == {
        "statusCode": 409,
        "code": "ORDER_ALREADY_SHIPPED",
        "message": "이미 발송된 주문이에요",
        "errors": [],
    }


def test_app_error_uses_defaults(client: TestClient) -> None:
    body = client.get("/default-message").json()
    assert body["code"] == "NOT_FOUND"
    assert body["message"] == "찾을 수 없어요"


def test_validation_error(client: TestClient) -> None:
    r = client.get("/items", params={"page": 0})
    assert r.status_code == 422
    body = r.json()
    assert body["statusCode"] == 422
    assert body["code"] == "VALIDATION_ERROR"
    assert body["errors"][0]["field"] == "query.page"


def test_missing_required_param(client: TestClient) -> None:
    body = client.get("/items").json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["errors"][0]["field"] == "query.page"


def test_unknown_path(client: TestClient) -> None:
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json() == {
        "statusCode": 404,
        "code": "NOT_FOUND",
        "message": "찾을 수 없어요",
        "errors": [],
    }


def test_method_not_allowed(client: TestClient) -> None:
    r = client.post("/conflict")
    assert r.status_code == 405
    assert r.json()["code"] == "METHOD_NOT_ALLOWED"
    assert "allow" in {k.lower() for k in r.headers}


def test_unexpected_error_hides_internal_detail(client: TestClient) -> None:
    r = client.get("/boom")
    assert r.status_code == 500
    assert r.json()["code"] == "INTERNAL_ERROR"
    assert "secret" not in r.text


def test_real_app_unknown_path_uses_error_format() -> None:
    r = TestClient(main_app).get("/api/v1/nope")
    assert r.status_code == 404
    assert r.json()["code"] == "NOT_FOUND"
