import logging
from pathlib import Path

from devpulse.config.settings import default_settings_path
from devpulse.privacy import SecretRedactionFilter, secure_file_permissions


def configure_logging() -> None:
    log_dir = default_settings_path().parent
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "devpulse.log"

    redaction_filter = SecretRedactionFilter()
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.addFilter(redaction_filter)
    stream_handler = logging.StreamHandler()
    stream_handler.addFilter(redaction_filter)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[file_handler, stream_handler],
    )
    secure_file_permissions(str(log_file))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
