import os

import pytest

from devpulse.integrations.opencode.client import OpenCodeClient
from devpulse.integrations.opencode.integration import OpenCodeIntegration


@pytest.mark.integration
def test_real_opencode_connection() -> None:
    if os.getenv("OPENCODE_INTEGRATION") != "1":
        pytest.skip("Set OPENCODE_INTEGRATION=1 to run")

    client = OpenCodeClient("http://127.0.0.1:49374")
    info = client.get_info()
    assert "version" in info

    integration = OpenCodeIntegration("http://127.0.0.1:49374")
    instances = integration.detect_instances()
    assert instances

    sessions = integration.list_sessions(instances[0])
    assert isinstance(sessions, list)
