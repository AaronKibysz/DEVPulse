import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from devpulse.integrations.opencode.integration import OpenCodeIntegration


def main() -> int:
    base_url = os.getenv("OPENCODE_URL", "http://127.0.0.1:49374")
    password = os.getenv("OPENCODE_PASSWORD")
    if not password:
        try:
            import json
            from pathlib import Path

            service_file = Path.home() / ".config" / "opencode" / "service.json"
            password = json.loads(service_file.read_text()).get("password")
        except Exception:
            password = None
    integration = OpenCodeIntegration(base_url, password)
    instances = integration.detect_instances()
    print(f"Instances: {len(instances)}")
    if not instances:
        return 1
    instance = instances[0]
    sessions = integration.list_sessions(instance)
    active_ids = integration.get_active_session_ids(instance)
    print(f"Sessions: {len(sessions)}")
    for session in sessions:
        print(
            f"- {session.id} | {session.title} | "
            f"model={session.model.name if session.model else 'unknown'} | "
            f"in={session.tokens.input} out={session.tokens.output} "
            f"cache={session.tokens.cache_read} | "
            f"{'active' if session.id in active_ids else 'inactive'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
