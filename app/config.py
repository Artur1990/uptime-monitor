from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class Target:
    name: str
    url: str

@dataclass(frozen=True)
class Settings:
    interval_seconds: int
    timeout_seconds: int
    targets: list[Target]

def load_settings(path: str | Path) -> Settings:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))

    targets = [Target(**t) for t in data["targets"]]
    return Settings(
        interval_seconds=int(data["interval_seconds"]),
        timeout_seconds=int(data["timeout_seconds"]),
        targets=targets,
    )
