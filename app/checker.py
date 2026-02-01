import asyncio
import logging
import time
import httpx
import os
from prometheus_client import Gauge
from app.config import Settings

logger = logging.getLogger("uptime.checker")

# Prometheus metrics
target_up = Gauge("uptime_target_up", "Target status (1=up, 0=down)", ["name", "url"])
target_latency_ms = Gauge("uptime_target_latency_ms", "Target latency in milliseconds", ["name", "url"])

HIGH_LATENCY_MS = int(os.getenv("HIGH_LATENCY_MS", "800"))  # log a warning if latency is above this threshold


class State:
    def __init__(self) -> None:
        self.last_results: dict[str, dict] = {}
        self.prev_ok: dict[str, bool] = {}


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

               # Structured logging (only on important events)
                prev = state.prev_ok.get(t.name)
                state.prev_ok[t.name] = ok
                

                extra = {
                    "target": t.name,
                    "url": t.url,
                    "ok": ok,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": err,
                }
                if prev is None:
                   logger.info("initial status", extra={"extra": extra})
                # Log state changes (UP->DOWN / DOWN->UP)
                if prev is not None and prev != ok:
                    if ok:
                        logger.info("target recovered", extra={"extra": extra})
                    else:
                        logger.error("target down", extra={"extra": extra})

                # Log request errors even if we didn't have a previous state
                if err:
                    logger.warning("request error", extra={"extra": extra})

                # Log high latency warnings
                if ok and latency_ms >= HIGH_LATENCY_MS:
                    logger.warning("high latency", extra={"extra": extra})

            await asyncio.sleep(settings.interval_seconds)
