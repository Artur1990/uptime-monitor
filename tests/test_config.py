from pathlib import Path
from app.config import load_settings


def test_load_settings(tmp_path: Path) -> None:
    p = tmp_path / "targets.yml"
    p.write_text(
        "interval_seconds: 5\n"
        "timeout_seconds: 3\n"
        "\n"
        "targets:\n"
        "  - name: example\n"
        "    url: https://example.com\n",
        encoding="utf-8",
    )

    s = load_settings(p)

    assert s.interval_seconds == 5
    assert s.timeout_seconds == 3
    assert len(s.targets) == 1
    assert s.targets[0].name == "example"
