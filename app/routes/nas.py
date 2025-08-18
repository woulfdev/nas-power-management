import re
import time
import datetime
import subprocess
from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel

from app.core.config import settings
from app.core.log import logger

router = APIRouter(
    prefix="/nas"
)

class SlackRequest(BaseModel):
    text: str

def power_off():
    out = subprocess.run(["/usr/bin/ipmitool", "-H", settings.IPMI_IP, "-U", settings.IPMI_USER, "-L", "OPERATOR", "-P", settings.IPMI_PASSWORD, "power", "soft"], capture_output=True)
    logger.info(out)

def power_on():
    out = subprocess.run(["/usr/bin/ipmitool", "-H", settings.IPMI_IP, "-U", settings.IPMI_USER, "-L", "OPERATOR", "-P", settings.IPMI_PASSWORD, "power", "on"], capture_output=True)
    logger.info(out)

@router.post("/alertservice")
async def handle_alert(
    request: SlackRequest,
    background_task: BackgroundTasks
):
    date = datetime.now()

    parsed = request.text.split("\n", 1)[1]
    parsed = parsed.replace("\n", "")
    parsed = parsed.replace("*", "")
    parsed = parsed.replace(" ", "")
    parsed = parsed.split(":")
    final = []
    for n in parsed:
        result = n.split(".")

        for y in result:
            final.append(y)

    # sanity check that alert starts with "New alert"
    if final[0] == "Newalert":
        # check if new alert is about completion of the replication task
        if final[1] == f'Replication"{settings.REPLICATION_NAME.replace(" ", "")}"succeeded':
            # check the time
            if time.strftime("%H:%M") >= settings.POWER_SAVING_TIME and time.strftime("%H:%M") < settings.POWER_ON_TIME:
                if date.weekday() != settings.EXCEPTION_DAY:
                    # turn of server in the background
                    background_task.add_task(power_off, settings)

@router.get("/power/state")
async def get_power_state():
    out = subprocess.run(["/usr/bin/ipmitool", "-H", settings.IPMI_IP, "-U", settings.IPMI_USER, "-L", "OPERATOR", "-P", settings.IPMI_PASSWORD, "power", "status"], capture_output=True).stdout.replace("\n", "")
    return out

@router.post("/power/off")
async def nas_power_off(
    background_task: BackgroundTasks
):
    background_task.add_task(power_off)

@router.post("/power/on")
async def nas_power_on(
    background_task: BackgroundTasks
):
    background_task.add_task(power_on)
