import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Settings:
    visible_metrics: List[str] = field(default_factory=lambda: ["model", "tokens", "context", "cost"])
    compact_mode: bool = True
    window_width: int = 420
    window_height: int = 320
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    refresh_interval_seconds: int = 10
    selected_instance: Optional[str] = None
    selected_session: Optional[str] = None
    opencode_url: Optional[str] = None
    cache_sensitive_data: bool = True
    sensitive_logs_authorized: bool = False
    sensitive_log_pin_hash: Optional[str] = None

    @classmethod
    def default(cls) -> "Settings":
        return cls()

    @classmethod
    def load(cls, path: Path) -> "Settings":
        if not path.exists():
            return cls.default()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (json.JSONDecodeError, TypeError, ValueError):
            return cls.default()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


def default_settings_path() -> Path:
    return Path.home() / ".devpulse" / "settings.json"
