from unittest.mock import patch

import httpx

from devpulse.integrations.opencode.client import OpenCodeClient


def _mock_response(data):
    return httpx.Response(200, json=data, request=httpx.Request("GET", "http://127.0.0.1:49374/api/info"))


def test_get_info() -> None:
    client = OpenCodeClient("http://127.0.0.1:49374")
    with patch("devpulse.integrations.opencode.client.httpx.get") as mock_get:
        mock_get.return_value = _mock_response({"version": "2.1.2"})
        result = client.get_info()
        assert result["version"] == "2.1.2"


def test_localhost_only() -> None:
    try:
        OpenCodeClient("http://example.com")
    except Exception as exc:
        assert "localhost" in str(exc).lower() or "127.0.0.1" in str(exc)
    else:
        raise AssertionError("Expected error for non-localhost URL")


def test_localhost_lookalike_rejected() -> None:
    for url in ("http://127.0.0.1.evil", "http://localhost.evil"):
        try:
            OpenCodeClient(url)
        except Exception:
            pass
        else:
            raise AssertionError(f"Expected error for {url}")
