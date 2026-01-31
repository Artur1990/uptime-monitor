import asyncio
import os
from fastapi import FastAPI
from app.config import load_settings
from app.checker import State, check_loop

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/targets.yml")

app = FastAPI(title="Uptime Monitor")
state = State()

@app.on_event("startup")
async def startup() -> None:
    settings = load_settings(CONFIG_PATH)
    asyncio.create_task(check_loop(settings, state))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/results")
def results():
    return state.last_results
