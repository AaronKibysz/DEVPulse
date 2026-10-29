from typing import Any, Dict, List, Optional

import httpx

from devpulse.domain.errors import IntegrationError


class OpenCodeClient:
    def __init__(self, base_url: str, password: Optional[str] = None) -> None:
        if not base_url.startswith("http://127.0.0.1") and not base_url.startswith("http://localhost"):
            raise IntegrationError("Only localhost connections are allowed")
        self.base_url = base_url.rstrip("/")
        self.password = password

    def _headers(self) -> dict:
        headers = {}
        if self.password:
            import base64

            token = base64.b64encode(f"opencode:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        return headers

    def _get(self, path: str, **kwargs: Any) -> Any:
        try:
            response = httpx.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                timeout=10.0,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise IntegrationError(str(exc)) from exc

    def get_info(self) -> Dict[str, Any]:
        return self._get("/api/info")

    def get_active_sessions(self) -> Dict[str, Any]:
        return self._get("/api/session/active")

    def list_sessions(self, limit: int = 50) -> Dict[str, Any]:
        return self._get("/api/session", params={"limit": limit, "order": "desc"})

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self._get(f"/api/session/{session_id}")

    def list_messages(self, session_id: str) -> Dict[str, Any]:
        return self._get(f"/api/session/{session_id}/message")

    def list_models(self) -> Dict[str, Any]:
        return self._get("/api/model")

    def list_projects(self) -> Any:
        return self._get("/api/project")
