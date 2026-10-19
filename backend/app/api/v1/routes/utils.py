from fastapi import APIRouter

from app.schemas import ApiResponse

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
def health_check() -> ApiResponse[bool]:
    return ApiResponse(data=True)
