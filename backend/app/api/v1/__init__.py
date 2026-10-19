from fastapi import APIRouter

from app.api.v1.routes import utils

router = APIRouter(prefix="/v1")
router.include_router(utils.router)
