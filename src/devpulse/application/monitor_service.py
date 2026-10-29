from typing import List, Optional, Set

from devpulse.domain.models import ContextMetrics, Instance, Session
from devpulse.integrations.opencode.client import OpenCodeClient
from devpulse.integrations.opencode.integration import OpenCodeIntegration
from devpulse.integrations.opencode.mapper import calculate_context


class MonitorService:
    def __init__(self, integration: OpenCodeIntegration) -> None:
        self.integration = integration

    def detect(self) -> List[Instance]:
        return self.integration.detect_instances()

    def sessions(self, instance: Instance) -> List[Session]:
        return self.integration.list_sessions(instance)

    def active_ids(self, instance: Instance) -> Set[str]:
        return self.integration.get_active_session_ids(instance)

    def session_details(self, instance: Instance, session_id: str) -> Session:
        return self.integration.get_session(instance, session_id)

    def context_for(self, session: Session, messages: list) -> ContextMetrics:
        return calculate_context(messages, session.model)
