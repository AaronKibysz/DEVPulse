import sys

from devpulse.logging import configure_logging

from PySide6.QtWidgets import QApplication

from devpulse.application.config_service import ConfigService
from devpulse.ui.main_window import MainWindow
from devpulse.ui.theme import apply_theme

def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    from pathlib import Path
    from PySide6.QtGui import QFontDatabase

    font_path = Path(__file__).resolve().parent / "resources" / "fonts" / "InterVariable.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
    config_service = ConfigService()
    apply_theme(app, config_service.settings)
    window = MainWindow(config_service)
    window.show()
    result = app.exec()
    config_service.close()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
