import sys

from devpulse.logging import configure_logging

from PySide6.QtWidgets import QApplication

from devpulse.application.config_service import ConfigService
from devpulse.ui.main_window import MainWindow


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    config_service = ConfigService()
    window = MainWindow(config_service)
    window.show()
    result = app.exec()
    config_service.close()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
