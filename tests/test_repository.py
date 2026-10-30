from pathlib import Path

from devpulse.domain.models import Session, TokenUsage
from devpulse.storage.database import Database
from devpulse.storage.repository import SnapshotRepository


def test_repository_roundtrip(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    repo = SnapshotRepository(db)
    session = Session(id="ses_1", project_id="proj_1", title="Test", tokens=TokenUsage(input=10))
    repo.save_sessions([session])
    rows = repo.load_latest()
    assert len(rows) == 1
    assert rows[0]["session_id"] == "ses_1"
    assert rows[0]["tokens"]["input"] == 10
    db.close()


def test_repository_mark_historical(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    repo = SnapshotRepository(db)
    session = Session(id="ses_1", project_id="proj_1", title="Test", tokens=TokenUsage(input=10))
    repo.save_sessions([session])
    repo.mark_historical()
    rows = repo.load_latest()
    assert rows[0]["is_historical"] is True
    db.close()
