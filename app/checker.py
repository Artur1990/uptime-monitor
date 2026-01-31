import asyncio
import time
import httpx
from app.config import Settings

class State:
    def __init__(self) -> None:
        self.last_results: dict[str, dict] = {}

async def check_loop(settings: Settings, state: State) -> None:
    async with httpx.AsyncClient(timeout=settings.timeout_seconds, follow_redirects=True) as client:
        while True:
            for t in settings.targets:
                started = time.time()
                ok = False
                status = None
                err = None
                try:
                    r = await client.get(t.url)
                    status = r.status_code
                    ok = 200 <= status < 400
                except httpx.RequestError as e:
                    err = str(e)

                latency_ms = int((time.time() - started) * 1000)
                state.last_results[t.name] = {
                    "url": t.url,
                    "ok": ok,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": err,
                    "ts": int(time.time()),
                }

            await asyncio.sleep(settings.interval_seconds)
