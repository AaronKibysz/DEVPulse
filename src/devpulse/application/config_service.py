from pathlib import Path
from typing import Optional

from devpulse.config.opencode_config import detect_opencode_config
from devpulse.config.settings import Settings, default_settings_path
from devpulse.privacy import RetryPolicy, register_secret, secure_file_permissions
from devpulse.storage.database import Database
from devpulse.storage.repository import SnapshotRepository


class ConfigService:
    def __init__(self, settings_path: Path | None = None, database_path: Path | None = None) -> None:
        self.settings_path = settings_path or default_settings_path()
        self.settings = Settings.load(self.settings_path)
        self.database = Database(database_path)
        self.repository = SnapshotRepository(self.database)
        self.password: Optional[str] = None
        self.config_source: str = "default"
        self.retry_policy = RetryPolicy()
        self._apply_detected_config()

    def _apply_detected_config(self) -> None:
        url, password, source = detect_opencode_config()
        if self.settings.opencode_url is None:
            self.settings.opencode_url = url
        self.password = password
        self.config_source = source
        if password:
            register_secret(password)

    def opencode_url(self) -> str:
        return self.settings.opencode_url or "http://127.0.0.1:49374"

    def set_opencode_config(self, url: str, password: Optional[str] = None) -> None:
        self.settings.opencode_url = url
        self.password = password
        if password:
            register_secret(password)

    def save_settings(self) -> None:
        self.settings.save(self.settings_path)
        secure_file_permissions(str(self.settings_path))

    def close(self) -> None:
        from devpulse.privacy import clear_registered_secrets

        clear_registered_secrets()
        self.database.close()
