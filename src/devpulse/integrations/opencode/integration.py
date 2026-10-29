from typing import List, Optional, Set

from devpulse.domain.models import ContextMetrics, Instance, Model, Session
from devpulse.integrations.base import IntegrationProvider
from devpulse.integrations.opencode.client import OpenCodeClient
from devpulse.integrations.opencode.mapper import (
    calculate_context,
    map_model,
    map_session,
    map_token_usage,
)


class OpenCodeIntegration(IntegrationProvider):
    def __init__(self, base_url: str, password: Optional[str] = None) -> None:
        self.client = OpenCodeClient(base_url, password)

    def detect_instances(self) -> List[Instance]:
        info = self.client.get_info()
        return [Instance(id="opencode-local", base_url=self.client.base_url, version=info.get("version"))]

    def list_sessions(self, instance: Instance) -> List[Session]:
        response = self.client.list_sessions()
        items = response.get("data", []) if isinstance(response, dict) else []
        models = {m.get("id"): map_model(m) for m in self._models()}
        sessions = []
        for item in items:
            model = models.get(item.get("model", {}).get("id"))
            sessions.append(map_session(item, model))
        return sessions

    def get_active_session_ids(self, instance: Instance) -> Set[str]:
        response = self.client.get_active_sessions()
        data = response.get("data", {}) if isinstance(response, dict) else {}
        return set(data.keys())

    def get_session(self, instance: Instance, session_id: str) -> Session:
        response = self.client.get_session(session_id)
        item = response.get("data", {}) if isinstance(response, dict) else {}
        models = {m.get("id"): map_model(m) for m in self._models()}
        model = models.get((item.get("model") or {}).get("id"))
        session = map_session(item, model)
        messages_response = self.client.list_messages(session_id)
        messages = messages_response.get("data", []) if isinstance(messages_response, dict) else []
        session.tokens = map_token_usage(item.get("tokens"))
        return session

    def get_context_metrics(self, session: Session) -> ContextMetrics:
        if not session.model:
            return ContextMetrics(source="unavailable")
        # Context metrics require message data; callers should pass messages.
        return ContextMetrics(source="unavailable")

    def get_session_with_context(self, instance: Instance, session_id: str) -> Session:
        session = self.get_session(instance, session_id)
        messages_response = self.client.list_messages(session_id)
        messages = messages_response.get("data", []) if isinstance(messages_response, dict) else []
        metrics = calculate_context(messages, session.model)
        # Store metrics temporarily on session is not part of model; return session only.
        return session

    def _models(self) -> List[dict]:
        response = self.client.list_models()
        if isinstance(response, dict):
            return response.get("data", [])
        return []
