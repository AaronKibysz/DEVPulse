from PySide6.QtCore import QThread, Signal

from devpulse.application.monitor_service import MonitorService
from devpulse.integrations.opencode.integration import OpenCodeIntegration


class RefreshWorker(QThread):
    finished = Signal(object, object)

    def __init__(self, base_url: str, password: str | None = None) -> None:
        super().__init__()
        self.base_url = base_url
        self.password = password

    def run(self) -> None:
        try:
            integration = OpenCodeIntegration(self.base_url, self.password)
            service = MonitorService(integration)
            instances = service.detect()
            if not instances:
                self.finished.emit([], "No OpenCode instance detected")
                return
            instance = instances[0]
            sessions = service.sessions(instance)
            active_ids = service.active_ids(instance)
            for session in sessions:
                session.active = session.id in active_ids
            self.finished.emit(sessions, None)
        except Exception as exc:  # noqa: BLE001
            self.finished.emit([], str(exc))
