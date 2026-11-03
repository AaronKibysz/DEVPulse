import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Settings:
    visible_metrics: List[str] = field(default_factory=lambda: ["model", "tokens", "context", "cost"])
    compact_mode: bool = True
    window_width: int = 260
    window_height: int = 190
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    refresh_interval_seconds: int = 10
    selected_instance: Optional[str] = None
    selected_session: Optional[str] = None
    data_source: str = "auto"
    opencode_url: Optional[str] = None
    cache_sensitive_data: bool = True
    sensitive_logs_authorized: bool = False
    sensitive_log_pin_hash: Optional[str] = None
    theme_mode: str = "neon"
    accent_color: str = "#ff00ff"
    glow_strength: str = "strong"
    font_size: str = "medium"
    reduce_motion: bool = False

    @classmethod
    def default(cls) -> "Settings":
        return cls()

    @classmethod
    def load(cls, path: Path) -> "Settings":
        if not path.exists():
            return cls.default()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            instance = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            # Clamp window size to sane defaults
            if instance.window_width < 100 or instance.window_width > 800:
                instance.window_width = 260
            if instance.window_height < 80 or instance.window_height > 800:
                instance.window_height = 190
            # Clamp position: if off-screen, reset to None (centered by OS)
            if instance.window_x is not None and (instance.window_x < -100 or instance.window_x > 4000):
                instance.window_x = None
            if instance.window_y is not None and (instance.window_y < -100 or instance.window_y > 4000):
                instance.window_y = None
            return instance
        except (json.JSONDecodeError, TypeError, ValueError):
            return cls.default()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


def default_settings_path() -> Path:
    return Path.home() / ".devpulse" / "settings.json"
