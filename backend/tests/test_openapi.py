"""/docs(OpenAPI) 가 실제 응답과 맞는지 확인한다."""

from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Query

from app.core.errors import error_responses
from app.main import app


def schemas() -> dict[str, Any]:
    return app.openapi()["components"]["schemas"]


def test_response_fields_with_defaults_are_required() -> None:
    # 기본값이 있어도 응답에는 항상 들어가므로 필수로 표시돼야 한다
    assert set(schemas()["ApiResponse_list_Kpi__"]["required"]) == {
        "statusCode",
        "code",
        "data",
    }
    assert "errors" in schemas()["ApiError"]["required"]
    assert "urgent" in schemas()["TodoItem"]["required"]
    assert "comparisons" in schemas()["Kpi"]["required"]


def test_dashboard_routes_document_only_possible_errors() -> None:
    responses = app.openapi()["paths"]["/api/v1/dashboard/kpis"]["get"]["responses"]
    assert set(responses) == {"200", "500"}
    assert responses["500"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ApiError"
    )


def test_error_responses_overrides_default_422() -> None:
    # 파라미터가 있는 라우트의 422 는 FastAPI 기본 형식 대신 ApiError 로 표시돼야 한다
    router = APIRouter()

    @router.get("/items", responses=error_responses(422))
    def items(page: Annotated[int, Query(ge=1)]) -> int:
        return page

    test_app = FastAPI()
    test_app.include_router(router)
    ref = test_app.openapi()["paths"]["/items"]["get"]["responses"]["422"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    assert ref.endswith("/ApiError")
