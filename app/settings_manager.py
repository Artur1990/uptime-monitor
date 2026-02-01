import asyncio
from app.config import Settings, Target

class SettingsManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._lock = asyncio.Lock()

    async def get(self) -> Settings:
        async with self._lock:
            return self._settings

    async def add_target(self, target: Target) -> bool:
        async with self._lock:
            for t in self._settings.targets:
                if t.name == target.name or t.url == target.url:
                    return False

            self._settings = Settings(
                interval_seconds=self._settings.interval_seconds,
                timeout_seconds=self._settings.timeout_seconds,
                targets=self._settings.targets + [target],
            )
            return True
