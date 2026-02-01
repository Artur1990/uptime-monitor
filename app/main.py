import asyncio
import os
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import load_settings
from app.checker import State, check_loop
from app.logging_utils import setup_logging

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/targets.yml")

app = FastAPI(title="Uptime Monitor")
state = State()


@app.on_event("startup")
async def startup() -> None:
    setup_logging()
    settings = load_settings(CONFIG_PATH)
    asyncio.create_task(check_loop(settings, state))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/results")
def results():
    return state.last_results


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
