import time
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.core.log import logger

router = APIRouter(
    prefix="/control"
)

@router.get("/power/offtime")
async def get_power_of_time():
    return