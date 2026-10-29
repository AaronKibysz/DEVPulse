from abc import ABC, abstractmethod
from typing import List, Optional, Set

from devpulse.domain.models import Instance, Session, Model, ContextMetrics


class IntegrationProvider(ABC):
    @abstractmethod
    def detect_instances(self) -> List[Instance]:
        raise NotImplementedError

    @abstractmethod
    def list_sessions(self, instance: Instance) -> List[Session]:
        raise NotImplementedError

    @abstractmethod
    def get_active_session_ids(self, instance: Instance) -> Set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_session(self, instance: Instance, session_id: str) -> Session:
        raise NotImplementedError

    @abstractmethod
    def get_context_metrics(self, session: Session) -> ContextMetrics:
        raise NotImplementedError
