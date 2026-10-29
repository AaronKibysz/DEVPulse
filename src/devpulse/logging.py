import logging
from pathlib import Path

from devpulse.config.settings import default_settings_path


def configure_logging() -> None:
    log_dir = default_settings_path().parent
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "devpulse.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
