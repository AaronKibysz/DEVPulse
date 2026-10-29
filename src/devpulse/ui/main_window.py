from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
)

from devpulse.ui.worker import RefreshWorker


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DevPulse")
        self.resize(420, 320)

        self.status_label = QLabel("Status: idle")
        self.refresh_button = QPushButton("Refresh")
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.output)

        self.refresh_button.clicked.connect(self._refresh)
        self.worker: RefreshWorker | None = None

    def _refresh(self) -> None:
        self.status_label.setText("Status: connecting...")
        self.refresh_button.setEnabled(False)
        self.worker = RefreshWorker("http://127.0.0.1:49374")
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, sessions, error) -> None:
        self.refresh_button.setEnabled(True)
        if error:
            self.status_label.setText("Status: error")
            self.output.setPlainText(str(error))
            return
        self.status_label.setText(f"Status: connected ({len(sessions)} sessions)")
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
