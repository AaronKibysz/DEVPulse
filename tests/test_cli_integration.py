import json
import subprocess

from devpulse.integrations.opencode.cli_integration import OpenCodeCliIntegration


def _completed(stdout: str, returncode: int = 0):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_cli_list_sessions_maps_export(monkeypatch) -> None:
    session_list = [
        {
            "id": "ses_1",
            "title": "Test",
            "updated": 10,
            "created": 1,
            "projectId": "proj_1",
            "directory": "C:\\repo",
        }
    ]
    export_payload = {
        "info": {
            "id": "ses_1",
            "projectID": "proj_1",
            "title": "Test",
            "cost": 1.5,
            "tokens": {"input": 10, "output": 2, "reasoning": 1, "cache": {"read": 3, "write": 0}},
            "model": {"id": "m1", "providerID": "p1"},
            "time": {"created": 1, "updated": 10},
        },
        "messages": [],
    }

    def fake_run(args, *_, **__):
        if "service" in args:
            return _completed("", returncode=1)
        if "api" in args:
            return _completed("[]")
        if "list" in args:
            return _completed(json.dumps(session_list))
        if "export" in args:
            return _completed("Exporting session...\n" + json.dumps(export_payload))
        raise AssertionError(args)

    monkeypatch.setattr("devpulse.integrations.opencode.cli_integration.subprocess.run", fake_run)
    integration = OpenCodeCliIntegration(working_directory="C:\\repo")
    sessions = integration.list_sessions(integration.detect_instances()[0])
    assert len(sessions) == 1
    assert sessions[0].id == "ses_1"
    assert sessions[0].tokens.input == 10
    assert sessions[0].cost == 1.5


def test_cli_active_session_is_latest(monkeypatch) -> None:
    session_list = [
        {"id": "ses_old", "updated": 1, "directory": "C:\\repo"},
        {"id": "ses_new", "updated": 2, "directory": "C:\\repo"},
    ]

    def fake_run(args, *_, **__):
        return _completed(json.dumps(session_list))

    monkeypatch.setattr("devpulse.integrations.opencode.cli_integration.subprocess.run", fake_run)
    integration = OpenCodeCliIntegration(working_directory="C:\\repo")
    assert integration.get_active_session_ids(integration.detect_instances()[0]) == {"ses_new"}