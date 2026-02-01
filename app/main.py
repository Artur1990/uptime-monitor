import asyncio
import os
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.logging_utils import setup_logging
from app.checker import State, check_loop
from app.settings_manager import SettingsManager
from app.storage import load_from_yaml

import logging
from app.telegram import send_telegram

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.telegram import send_telegram

from app.telegram_bot import telegram_command_loop

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/targets.yml")

app = FastAPI(title="Uptime Monitor")
state = State()
settings_manager: SettingsManager | None = None

logger = logging.getLogger("uptime.telegram_status")

TELEGRAM_STATUS_INTERVAL_SECONDS = int(os.getenv("TELEGRAM_STATUS_INTERVAL_SECONDS", "0"))

TELEGRAM_STATUS_TIME = os.getenv("TELEGRAM_STATUS_TIME", "")  # "HH:MM" or empty
TELEGRAM_TIMEZONE = os.getenv("TELEGRAM_TIMEZONE", "Asia/Jerusalem")

def build_status_text(state: State) -> str:
    results = state.last_results
    if not results:
        return "ℹ️ Status: no data yet"
    up = sum(1 for r in results.values() if r.get("ok") is True)
    down = sum(1 for r in results.values() if r.get("ok") is False)

    lines = [f"📊 Status: UP={up} DOWN={down}"]
    for name, r in sorted(results.items()):
        icon = "✅" if r.get("ok") else "❌"
        lat = r.get("latency_ms")
        status = r.get("status")
        lines.append(f"{icon} {name} | status={status} | {lat}ms")
    return "\n".join(lines)

async def telegram_daily_status_loop(state: State) -> None:
    if not TELEGRAM_STATUS_TIME:
        return

    hh, mm = TELEGRAM_STATUS_TIME.split(":")
    hour = int(hh)
    minute = int(mm)
    tz = ZoneInfo(TELEGRAM_TIMEZONE)

    while True:
        now = datetime.now(tz)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)

        sleep_seconds = (target - now).total_seconds()
        await asyncio.sleep(sleep_seconds)

        await send_telegram(build_status_text(state))


async def telegram_status_loop(state: State) -> None:
    """Send periodic status summary to Telegram (if enabled)."""
    if TELEGRAM_STATUS_INTERVAL_SECONDS <= 0:
        return

    while True:
        try:
            results = state.last_results
            if not results:
                await send_telegram("ℹ️ Status: no data yet")
            else:
                up = sum(1 for r in results.values() if r.get("ok") is True)
                down = sum(1 for r in results.values() if r.get("ok") is False)

                lines = [f"📊 Status: UP={up} DOWN={down}"]
                for name, r in sorted(results.items()):
                    icon = "✅" if r.get("ok") else "❌"
                    lat = r.get("latency_ms")
                    status = r.get("status")
                    lines.append(f"{icon} {name} | status={status} | {lat}ms")

                await send_telegram("\n".join(lines))
        except Exception as e:
            logger.warning("status loop failed", extra={"extra": {"error": str(e)}})

        await asyncio.sleep(TELEGRAM_STATUS_INTERVAL_SECONDS)


@app.on_event("startup")
async def startup() -> None:
    global settings_manager
    setup_logging()

    # Load settings from YAML and wrap them with SettingsManager
    settings = load_from_yaml()
    settings_manager = SettingsManager(settings)
    asyncio.create_task(check_loop(settings_manager, state))
    asyncio.create_task(telegram_status_loop(state))
    asyncio.create_task(telegram_daily_status_loop(state))
    asyncio.create_task(telegram_command_loop(lambda: build_status_text(state)))


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/results")
def results():
    return state.last_results

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
