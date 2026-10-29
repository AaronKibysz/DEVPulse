from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
)

from devpulse.application.config_service import ConfigService
from devpulse.ui.worker import RefreshWorker


class MainWindow(QWidget):
    def __init__(self, config_service: ConfigService) -> None:
        super().__init__()
        self.config_service = config_service
        settings = config_service.settings

        self.setWindowTitle("DevPulse")
        self.resize(settings.window_width, settings.window_height)
        if settings.window_x is not None and settings.window_y is not None:
            self.move(settings.window_x, settings.window_y)

        self.status_label = QLabel("Status: ready")
        self.last_updated_label = QLabel("Last updated: never")
        self.refresh_button = QPushButton("Refresh")
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.last_updated_label)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.output)

        self.refresh_button.clicked.connect(self._refresh)
        self.worker: RefreshWorker | None = None
        self._refresh_interval = settings.refresh_interval_seconds * 1000
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_if_idle)
        self._timer.start(self._refresh_interval)

        self._load_cached_data()

    def _load_cached_data(self) -> None:
        rows = self.config_service.repository.load_latest()
        if not rows:
            return
        lines = []
        for row in rows:
            suffix = " (historical)" if row.get("is_historical") else ""
            lines.append(f"{row['session_id']} | {row['title']} | {row['model']}{suffix}")
        self.output.setPlainText("\n".join(lines))

    def _refresh_if_idle(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            return
        self._refresh()

    def _refresh(self) -> None:
        self.status_label.setText("Status: connecting...")
        self.refresh_button.setEnabled(False)
        self.worker = RefreshWorker("http://127.0.0.1:49374")
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, sessions, error) -> None:
        self.refresh_button.setEnabled(True)
        if error:
            self._refresh_interval = min(self._refresh_interval * 2, 60000)
            self._timer.setInterval(self._refresh_interval)
            self.status_label.setText("Status: error")
            cached = self.config_service.repository.load_latest()
            if cached:
                self.status_label.setText("Status: using cached data")
                lines = []
                for row in cached:
                    lines.append(f"{row['session_id']} | {row['title']} (historical)")
                self.output.setPlainText("\n".join(lines))
            else:
                self.output.setPlainText(str(error))
            return
        from datetime import datetime
        self.status_label.setText(f"Status: connected ({len(sessions)} sessions)")
        self.last_updated_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        lines = []
        for session in sessions:
            active = "active" if session.active else "inactive"
            model = session.model.name if session.model else "unknown"
            lines.append(
                f"{session.id} | {session.title} | {model} | "
                f"in={session.tokens.input} out={session.tokens.output} "
                f"cache={session.tokens.cache_read} | {active}"
            )
        self.output.setPlainText("\n".join(lines))
        self._refresh_interval = self.config_service.settings.refresh_interval_seconds * 1000
        self._timer.setInterval(self._refresh_interval)
        self.config_service.repository.save_sessions(sessions, is_historical=False)
        self.config_service.settings.selected_session = sessions[0].id if sessions else None

    def closeEvent(self, event) -> None:  # type: ignore[override]
        settings = self.config_service.settings
        settings.window_width = self.width()
        settings.window_height = self.height()
        settings.window_x = self.x()
        settings.window_y = self.y()
        self._timer.stop()
        self.config_service.save_settings()
        self.config_service.close()
        super().closeEvent(event)
