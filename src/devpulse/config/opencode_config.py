import json
import os
from pathlib import Path
from typing import Optional, Tuple

from devpulse.domain.errors import IntegrationError
from devpulse.integrations.opencode.client import OpenCodeClient


def detect_opencode_config() -> Tuple[Optional[str], Optional[str], str]:
    url = os.getenv("OPENCODE_URL")
    password = os.getenv("OPENCODE_PASSWORD")
    source = "environment" if url or password else ""

    if url is None or password is None:
        service_file = Path.home() / ".config" / "opencode" / "service.json"
        try:
            data = json.loads(service_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                if url is None:
                    if isinstance(data.get("url"), str):
                        url = data["url"]
                    elif isinstance(data.get("base_url"), str):
                        url = data["base_url"]
                    elif data.get("port") is not None:
                        url = f"http://127.0.0.1:{data['port']}"
                if password is None and isinstance(data.get("password"), str):
                    password = data["password"]
                if not source:
                    source = "service.json"
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    if url is None:
        url = "http://127.0.0.1:49374"
        if not source:
            source = "default"

    OpenCodeClient(url)  # Validate localhost before returning.
    return url, password, source or "default"
