import re
from pathlib import Path
from datetime import datetime, time
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

def power_off() -> None:
    out = subprocess.run(["/usr/bin/ipmitool", "-H", settings.IPMI_IP, "-U", settings.IPMI_USER, "-L", "OPERATOR", "-P", settings.IPMI_PASSWORD, "power", "soft"], capture_output=True)
    logger.info(out.stderr)

def power_on() -> None:
    out = subprocess.run(["/usr/bin/ipmitool", "-H", settings.IPMI_IP, "-U", settings.IPMI_USER, "-L", "OPERATOR", "-P", settings.IPMI_PASSWORD, "power", "on"], capture_output=True)
    logger.info(out.stderr)

def alert_handler(alert: str) -> None:
    date = datetime.now()

    if settings.LOG_ALERTS:
        try:
            file_size = Path("./alert_log.log").stat().st_size
            if file_size > 1000000:
                with open("./alert_log.log", "w") as f:
                    f.write("")
        except FileNotFoundError:
            logger.info("No alert log file.")
        except PermissionError:
            logger.info("No alert log file permission.")

        with open('./alert_log.log', "a") as f:
            f.write("\n")
            f.write(f'{time.strftime("%H:%M:%S")}:\n')
            f.write(alert)

    text = alert.replace(" ", "")
    text = text.replace("*", "")
    text = text.lower()

    parsed = text.split("\n")

    for n in parsed:
        if "thefollowingalerthasbeencleared" in n:
            break

        if "currentalerts" in n:
            break

        if f'replication"{settings.REPLICATION_NAME.lower().replace(" ", "")}"succeeded' in n:
            off_time_string = settings.POWER_SAVING_TIME.split(":")
            on_time_string = settings.POWER_ON_TIME.split(":")

            off_time = time(off_time_string[0], off_time_string[1])
            on_time = time(on_time_string[0], on_time_string[1])

            if datetime.now().time() >= off_time and datetime.now().time < on_time and date.weekday() != settings.EXCEPTION_DAY:
                power_off()
                
            break

# #####################################################################

@router.post("/alertservice")
async def handle_alert(
    request: SlackRequest,
    background_task: BackgroundTasks
):
    background_task.add_task(alert_handler, request.text)
    

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
