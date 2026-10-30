import os
from pathlib import Path

from devpulse.config.opencode_config import detect_opencode_config


def test_detect_opencode_config_default(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("OPENCODE_URL", raising=False)
    monkeypatch.delenv("OPENCODE_PASSWORD", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    url, password, source = detect_opencode_config()
    assert url == "http://127.0.0.1:49374"
    assert password is None
    assert source == "default"


def test_detect_opencode_config_from_service_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("OPENCODE_URL", raising=False)
    monkeypatch.delenv("OPENCODE_PASSWORD", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    service_dir = tmp_path / ".config" / "opencode"
    service_dir.mkdir(parents=True)
    (service_dir / "service.json").write_text('{"port": 5000, "password": "secret"}', encoding="utf-8")
    url, password, source = detect_opencode_config()
    assert url == "http://127.0.0.1:5000"
    assert password == "secret"
    assert source == "service.json"
