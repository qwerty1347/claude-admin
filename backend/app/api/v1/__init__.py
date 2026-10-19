from fastapi import APIRouter

from app.api.v1.routes import dashboard, utils

router = APIRouter(prefix="/v1")
router.include_router(utils.router)
router.include_router(dashboard.router)
