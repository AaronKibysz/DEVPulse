import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from devpulse.domain.errors import IntegrationError
from devpulse.domain.models import ContextMetrics, Instance, Session
from devpulse.integrations.base import IntegrationProvider
from devpulse.integrations.opencode.mapper import (
    calculate_context,
    map_model,
    map_session,
    map_token_usage,
)


class OpenCodeCliIntegration(IntegrationProvider):
    def __init__(self, working_directory: str | None = None, max_sessions: int = 10) -> None:
        self.working_directory = working_directory or os.getcwd()
        self.max_sessions = max_sessions
        self._export_cache: dict[tuple[str, int], dict[str, Any]] = {}

    def _executable(self) -> str:
        cmd_path = shutil.which("opencode")
        if cmd_path:
            candidate = Path(cmd_path).resolve().parent / "node_modules" / "opencode-ai" / "bin" / "opencode.exe"
            if candidate.exists():
                return str(candidate)
        exe_path = shutil.which("opencode.exe")
        if exe_path:
            return exe_path
        if cmd_path:
            return cmd_path
        raise IntegrationError("OpenCode CLI is not available")

    def _run(self, args: List[str]) -> str:
        try:
            result = subprocess.run(
                [self._executable(), *args],
                capture_output=True,
                text=True,
                encoding="utf-8-sig",
                timeout=15.0,
                cwd=self.working_directory,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise IntegrationError(str(exc)) from exc
        if result.returncode != 0:
            raise IntegrationError(result.stderr.strip() or "OpenCode CLI command failed")
        return result.stdout

    def _json_from_output(self, output: str) -> Any:
        candidates = [index for index in (output.find("["), output.find("{")) if index != -1]
        if not candidates:
            raise IntegrationError("OpenCode CLI did not return JSON")
        start = min(candidates)
        return json.loads(output[start:])

    def _list_raw_sessions(self) -> List[Dict[str, Any]]:
        output = self._run(["session", "list", "--format", "json"])
        data = self._json_from_output(output)
        if not isinstance(data, list):
            raise IntegrationError("Unexpected OpenCode session list")
        return sorted(data, key=lambda item: item.get("updated", 0), reverse=True)[: self.max_sessions]

    def _export(self, session_id: str, updated_at: int) -> Dict[str, Any]:
        cache_key = (session_id, updated_at)
        cached = self._export_cache.get(cache_key)
        if cached is not None:
            return cached
        output = self._run(["export", session_id])
        data = self._json_from_output(output)
        if not isinstance(data, dict):
            raise IntegrationError("Unexpected OpenCode export")
        self._export_cache[cache_key] = data
        return data

    def detect_instances(self) -> List[Instance]:
        self._executable()
        return [Instance(id="opencode-cli", base_url="cli://local", version=None)]

    def list_sessions(self, instance: Instance) -> List[Session]:
        sessions: List[Session] = []
        for item in self._list_raw_sessions():
            session_id = str(item.get("id", ""))
            if not session_id:
                continue
            if item.get("directory") and item.get("directory") != self.working_directory:
                continue
            try:
                data = self._export(session_id, int(item.get("updated", 0) or 0))
                info = data.get("info", {}) if isinstance(data, dict) else {}
                model = map_model(info.get("model")) if isinstance(info.get("model"), dict) else None
                session = map_session(info if info else item, model)
                session.tokens = map_token_usage(info.get("tokens"))
                sessions.append(session)
            except IntegrationError:
                sessions.append(
                    Session(
                        id=session_id,
                        project_id=str(item.get("projectId", "")),
                        title=str(item.get("title", session_id)),
                        updated_at=item.get("updated"),
                    )
                )
        return sessions

    def get_active_session_ids(self, instance: Instance) -> set[str]:
        try:
            sessions = self._list_raw_sessions()
        except IntegrationError:
            return set()
        matching = [item for item in sessions if item.get("directory") == self.working_directory]
        candidates = matching or sessions
        if not candidates:
            return set()
        latest = max(candidates, key=lambda item: item.get("updated", 0))
        return {str(latest.get("id"))}

    def get_session(self, instance: Instance, session_id: str) -> Session:
        data = self._export(session_id, 0)
        info = data.get("info", {}) if isinstance(data, dict) else {}
        model = map_model(info.get("model")) if isinstance(info.get("model"), dict) else None
        session = map_session(info, model)
        session.tokens = map_token_usage(info.get("tokens"))
        return session

    def list_messages(self, instance: Instance, session_id: str) -> List[dict]:
        try:
            data = self._export(session_id, 0)
        except IntegrationError:
            return []
        messages = data.get("messages", []) if isinstance(data, dict) else []
        result: List[dict] = []
        for message in messages:
            info = message.get("info", {}) if isinstance(message, dict) else {}
            role = info.get("role")
            if role not in {"user", "assistant"}:
                continue
            msg_type = "assistant" if role == "assistant" else "user"
            result.append({"type": msg_type, "tokens": info.get("tokens")})
        return result

    def get_context_metrics(self, session: Session) -> ContextMetrics:
        return ContextMetrics(source="unavailable")