from PySide6.QtCore import QThread, Signal

from devpulse.application.monitor_service import MonitorService
from devpulse.domain.models import ContextMetrics
from devpulse.integrations.opencode.integration import OpenCodeIntegration
from devpulse.logging import get_logger

logger = get_logger(__name__)


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
                logger.info("No OpenCode instance detected")
                self.finished.emit([], "No OpenCode instance detected")
                return
            instance = instances[0]
            sessions = service.sessions(instance)
            active_ids = service.active_ids(instance)
            for session in sessions:
                session.active = session.id in active_ids
                try:
                    session.context_metrics = service.context_for(instance, session)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Context calculation failed for %s: %s", session.id, exc)
                    session.context_metrics = ContextMetrics(source="unavailable")
            logger.info("Refreshed %d sessions", len(sessions))
            self.finished.emit(sessions, None)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Refresh failed: %s", exc)
            self.finished.emit([], str(exc))
