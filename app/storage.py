from pathlib import Path
import yaml
from app.config import Settings, Target

CONFIG_FILE = Path("config/targets.yml")

def load_from_yaml(path: Path = CONFIG_FILE) -> Settings:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    targets = [Target(**t) for t in data.get("targets", [])]
    return Settings(
        interval_seconds=int(data.get("interval_seconds", 5)),
        timeout_seconds=int(data.get("timeout_seconds", 3)),
        targets=targets,
    )

def save_to_yaml(settings: Settings, path: Path = CONFIG_FILE) -> None:
    data = {
        "interval_seconds": settings.interval_seconds,
        "timeout_seconds": settings.timeout_seconds,
        "targets": [{"name": t.name, "url": t.url} for t in settings.targets],
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
