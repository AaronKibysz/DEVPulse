from pathlib import Path

from devpulse.config.settings import Settings, default_settings_path
from devpulse.storage.database import Database
from devpulse.storage.repository import SnapshotRepository


class ConfigService:
    def __init__(self, settings_path: Path | None = None, database_path: Path | None = None) -> None:
        self.settings_path = settings_path or default_settings_path()
        self.settings = Settings.load(self.settings_path)
        self.database = Database(database_path)
        self.repository = SnapshotRepository(self.database)

    def save_settings(self) -> None:
        self.settings.save(self.settings_path)

    def close(self) -> None:
        self.database.close()
