from fastapi import APIRouter

from app.routes import nas, control
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(nas.router)
api_router.include_router(control.router)
