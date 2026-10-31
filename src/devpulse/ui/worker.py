import time
from typing import Optional

from devpulse.application.monitor_service import MonitorService
from devpulse.domain.models import ContextMetrics
from devpulse.integrations.opencode.cli_integration import OpenCodeCliIntegration
from devpulse.integrations.opencode.integration import OpenCodeIntegration
from devpulse.logging import get_logger
from PySide6.QtCore import QThread, Signal


logger = get_logger(__name__)

_HTTP_UNAVAILABLE_UNTIL: float = 0.0
_HTTP_CACHE_SECONDS = 300.0


class RefreshWorker(QThread):
    finished = Signal(object, object, object, object)

    def __init__(
        self,
        base_url: str,
        password: str | None = None,
        selected_instance_id: str | None = None,
        data_source: str = "auto",
    ) -> None:
        super().__init__()
        self.base_url = base_url
        self.password = password
        self.selected_instance_id = selected_instance_id
        self.data_source = data_source

    def run(self) -> None:
        try:
            integration = self._create_integration()
            service = MonitorService(integration)
            instances = service.detect()
            if not instances:
                logger.info("No OpenCode instance detected")
                self.finished.emit([], [], None, "No OpenCode instance detected")
                return
            instance = self._select_instance(instances)
            sessions = service.sessions(instance)
            active_ids = service.active_ids(instance)
            for session in sessions:
                session.active = session.id in active_ids
                try:
                    session.context_metrics = service.context_for(instance, session)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Context calculation failed for %s: %s", session.id, exc)
                    session.context_metrics = ContextMetrics(source="unavailable")
            logger.info("Refreshed %d sessions from %s", len(sessions), instance.id)
            self.finished.emit(instances, sessions, instance.id, None)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Refresh failed: %s", exc)
            self.finished.emit([], [], None, str(exc))

    def _create_integration(self):
        if self.data_source == "cli":
            return OpenCodeCliIntegration()
        if self.data_source == "http":
            return OpenCodeIntegration(self.base_url, self.password)
        global _HTTP_UNAVAILABLE_UNTIL
        if time.monotonic() < _HTTP_UNAVAILABLE_UNTIL:
            return OpenCodeCliIntegration()
        try:
            integration = OpenCodeIntegration(self.base_url, self.password)
            integration.detect_instances()
            _HTTP_UNAVAILABLE_UNTIL = 0.0
            return integration
        except Exception as exc:  # noqa: BLE001
            logger.debug("HTTP source unavailable, falling back to CLI: %s", exc)
            _HTTP_UNAVAILABLE_UNTIL = time.monotonic() + _HTTP_CACHE_SECONDS
            return OpenCodeCliIntegration()

    def _select_instance(self, instances):
        if self.selected_instance_id is not None:
            for instance in instances:
                if instance.id == self.selected_instance_id:
                    return instance
        return instances[0]