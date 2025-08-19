from typing import Annotated
from fastapi import FastAPI

from app.routes.router import api_router
from app.core.config import settings
from app.core.log import logger

app = FastAPI(
    version=settings.APP_VERSION
)

app.include_router(api_router)

@app.get("/", status_code=418)
async def root():
    return {"description":"I'm a teapot"}