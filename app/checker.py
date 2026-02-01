import asyncio
import time
import httpx
from prometheus_client import Gauge
from app.config import Settings

# Prometheus metrics
target_up = Gauge("uptime_target_up", "Target status (1=up, 0=down)", ["name", "url"])
target_latency_ms = Gauge("uptime_target_latency_ms", "Target latency in milliseconds", ["name", "url"])

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

                # Update in-memory state
                state.last_results[t.name] = {
                    "url": t.url,
                    "ok": ok,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": err,
                    "ts": int(time.time()),
                }

                # Update Prometheus metrics
                target_up.labels(name=t.name, url=t.url).set(1 if ok else 0)
                target_latency_ms.labels(name=t.name, url=t.url).set(latency_ms)

            await asyncio.sleep(settings.interval_seconds)
