from pathlib import Path

from devpulse.config.settings import Settings


def test_settings_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    settings = Settings(window_width=500, window_height=400)
    settings.save(path)
    loaded = Settings.load(path)
    assert loaded.window_width == 500
    assert loaded.window_height == 400


def test_settings_default_on_invalid(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{invalid", encoding="utf-8")
    loaded = Settings.load(path)
    assert loaded == Settings.default()
