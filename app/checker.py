import asyncio
import logging
import os
import time

import httpx
from prometheus_client import Gauge

from app.settings_manager import SettingsManager
from app.telegram import send_telegram

logger = logging.getLogger("uptime.checker")

# Prometheus metrics
target_up = Gauge(
    "uptime_target_up",
    "Target status (1=up, 0=down)",
    ["name", "url"],
)

target_latency_ms = Gauge(
    "uptime_target_latency_ms",
    "Target latency in milliseconds",
    ["name", "url"],
)

HIGH_LATENCY_MS = int(os.getenv("HIGH_LATENCY_MS", "800"))


class State:
    def __init__(self) -> None:
        self.last_results: dict[str, dict] = {}
        self.prev_ok: dict[str, bool] = {}


async def check_loop(settings_manager: SettingsManager, state: State) -> None:
    while True:
        settings = await settings_manager.get()

        async with httpx.AsyncClient(
            timeout=settings.timeout_seconds,
            follow_redirects=True,
        ) as client:
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

                # Save last result
                state.last_results[t.name] = {
                    "url": t.url,
                    "ok": ok,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": err,
                    "ts": int(time.time()),
                }

                # Update metrics
                target_up.labels(name=t.name, url=t.url).set(1 if ok else 0)
                target_latency_ms.labels(name=t.name, url=t.url).set(latency_ms)

                extra = {
                    "target": t.name,
                    "url": t.url,
                    "ok": ok,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": err,
                }

                prev = state.prev_ok.get(t.name)
                state.prev_ok[t.name] = ok

                # First run log
                if prev is None:
                    logger.info("initial status", extra={"extra": extra})

                # State change (DOWN / RECOVERED)
                if prev is not None and prev != ok:
                    if ok:
                        logger.info("target recovered", extra={"extra": extra})
                        await send_telegram(
                            f"✅ RECOVERED: {t.name}\n"
                            f"{t.url}\n"
                            f"status={status} latency={latency_ms}ms"
                        )
                    else:
                        logger.error("target down", extra={"extra": extra})
                        await send_telegram(
                            f"❌ DOWN: {t.name}\n"
                            f"{t.url}\n"
                            f"status={status} error={err} latency={latency_ms}ms"
                        )

                # Request error (log only)
                if err:
                    logger.warning("request error", extra={"extra": extra})

                # High latency (log only)
                if ok and latency_ms >= HIGH_LATENCY_MS:
                    logger.warning("high latency", extra={"extra": extra})

        await asyncio.sleep(settings.interval_seconds)
