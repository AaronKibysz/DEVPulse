from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap, QColor
import pyqtgraph as pg
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QComboBox,
    QTabWidget,
    QLineEdit,
    QSpinBox,
    QMessageBox,
    QInputDialog,
    QCheckBox,
    QMenu,
    QSystemTrayIcon,
)

from devpulse.application.config_service import ConfigService
from devpulse.application.metric_history import MetricHistory
from devpulse.ui.charts import (
    context_trend_points,
    context_values,
    sample_from_session,
    token_bar_values,
)
from devpulse.ui.pie_chart import PieChartWidget
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

        self.sessions = []
        self.instances = []
        self.metric_history = MetricHistory()
        self._password_prompted = False

        self.tabs = QTabWidget()
        self.monitor_tab = QWidget()
        self.config_tab = QWidget()
        self.tabs.addTab(self.monitor_tab, "Monitor")
        self.tabs.addTab(self.config_tab, "Configuration")

        self._build_monitor_tab()
        self._build_config_tab()

        self.footer_label = QLabel("")
        self.footer_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(self.footer_label)

        self.refresh_button.clicked.connect(self._refresh)
        self.mode_button.clicked.connect(self._toggle_mode)
        self.instance_combo.currentIndexChanged.connect(self._on_instance_selected)
        self.session_combo.currentIndexChanged.connect(self._on_session_selected)
        self.save_config_button.clicked.connect(self._save_config)
        self.worker: RefreshWorker | None = None
        self._refresh_interval = settings.refresh_interval_seconds * 1000
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_if_idle)
        self._timer.start(self._refresh_interval)

        self._load_cached_data()
        self._confirm_detected_config()
        self._apply_mode()
        self._setup_tray()

    def _build_monitor_tab(self) -> None:
        self.status_label = QLabel("Status: ready")
        self.last_updated_label = QLabel("Last updated: never")
        self.refresh_button = QPushButton("Refresh")
        self.mode_button = QPushButton("Toggle mode")
        self.instance_label = QLabel("Instance:")
        self.instance_combo = QComboBox()
        self.instance_combo.setEnabled(False)
        self.session_label = QLabel("Session:")
        self.session_combo = QComboBox()
        self.session_combo.setEnabled(False)
        self.details_label = QLabel("No session selected")
        self.compact_chart_view = PieChartWidget()
        self.compact_chart_view.setMinimumHeight(120)
        self.context_pie_view = PieChartWidget()
        self.context_pie_view.setMinimumHeight(160)
        self.token_chart_view = pg.PlotWidget()
        self.token_chart_view.setMinimumHeight(180)
        self.trend_chart_view = pg.PlotWidget()
        self.trend_chart_view.setMinimumHeight(180)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout(self.monitor_tab)
        layout.addWidget(self.status_label)
        layout.addWidget(self.last_updated_label)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.mode_button)
        layout.addWidget(self.instance_label)
        layout.addWidget(self.instance_combo)
        layout.addWidget(self.session_label)
        layout.addWidget(self.session_combo)
        layout.addWidget(self.details_label)
        layout.addWidget(self.compact_chart_view)
        layout.addWidget(self.context_pie_view)
        layout.addWidget(self.token_chart_view)
        layout.addWidget(self.trend_chart_view)
        layout.addWidget(self.output)

    def _build_config_tab(self) -> None:
        settings = self.config_service.settings
        self.url_edit = QLineEdit(self.config_service.opencode_url())
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Leave empty to use automatic authentication")
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(300)
        self.interval_spin.setValue(settings.refresh_interval_seconds)
        self.cache_sensitive_checkbox = QCheckBox("Cache sensitive data in memory")
        self.cache_sensitive_checkbox.setChecked(settings.cache_sensitive_data)
        self.sensitive_logs_checkbox = QCheckBox("Authorize sensitive logs")
        self.sensitive_logs_checkbox.setChecked(settings.sensitive_logs_authorized)
        self.data_source_combo = QComboBox()
        self.data_source_combo.addItems(["auto", "http", "cli"])
        self.data_source_combo.setCurrentText(settings.data_source)
        self.save_config_button = QPushButton("Save configuration")

        layout = QVBoxLayout(self.config_tab)
        layout.addWidget(QLabel("OpenCode URL"))
        layout.addWidget(self.url_edit)
        layout.addWidget(QLabel("Password (optional, not stored in plain text)"))
        layout.addWidget(self.password_edit)
        layout.addWidget(QLabel("Refresh interval (seconds)"))
        layout.addWidget(self.interval_spin)
        layout.addWidget(self.cache_sensitive_checkbox)
        layout.addWidget(self.sensitive_logs_checkbox)
        layout.addWidget(QLabel("Data source"))
        layout.addWidget(self.data_source_combo)
        layout.addWidget(self.save_config_button)
        layout.addStretch(1)

    def _confirm_detected_config(self) -> None:
        source = self.config_service.config_source
        url = self.config_service.opencode_url()
        if source in {"environment", "service.json"}:
            answer = QMessageBox.question(
                self,
                "OpenCode configuration detected",
                f"Use automatically detected configuration?\n\nURL: {url}\nSource: {source}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if answer == QMessageBox.No:
                self.tabs.setCurrentWidget(self.config_tab)
                self.footer_label.setText("Automatic configuration was not applied. You can edit it in the Configuration tab.")
            else:
                self.footer_label.setText(f"Using automatically detected configuration from {source}.")
        else:
            self.footer_label.setText("No OpenCode configuration was detected. Use the Configuration tab or environment variables.")

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
        if not self.config_service.retry_policy.allow_retry():
            self.status_label.setText("Status: retry blocked")
            self.footer_label.setText("Automatic retries are paused after repeated failures. Use Refresh to try again.")
            return
        self.status_label.setText("Status: connecting...")
        self.refresh_button.setEnabled(False)
        url = self.config_service.opencode_url()
        password = self.config_service.password
        self.worker = RefreshWorker(
            url,
            password,
            self.config_service.settings.selected_instance,
            self.config_service.settings.data_source,
        )
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, instances, sessions, selected_instance_id, error) -> None:
        self.refresh_button.setEnabled(True)
        if error:
            self.config_service.retry_policy.record_failure()
            if self.config_service.retry_policy.blocked:
                self._timer.stop()
                self.footer_label.setText("Access failed repeatedly. Automatic retries are paused. Use Refresh or update configuration to try again.")
            self._refresh_interval = min(self._refresh_interval * 2, 60000)
            self._timer.setInterval(self._refresh_interval)
            self.status_label.setText("Status: error")
            cached = self.config_service.repository.load_latest()
            if cached:
                self.config_service.repository.mark_historical()
                self.status_label.setText("Status: using cached data")
                lines = []
                for row in cached:
                    lines.append(f"{row['session_id']} | {row['title']} (historical)")
                self.output.setPlainText("\\n".join(lines))
                self.footer_label.setText("OpenCode is unavailable. Showing cached data.")
            else:
                self.output.setPlainText(str(error))
                self.footer_label.setText(str(error))
            if self._is_auth_error(error) and not self._password_prompted:
                self._prompt_password_once()
            return

        from datetime import datetime

        self.sessions = sessions
        self.instances = instances
        if selected_instance_id is not None:
            self.config_service.settings.selected_instance = selected_instance_id
        self.config_service.retry_policy.record_success()
        self.status_label.setText(f"Status: connected ({len(sessions)} sessions)")
        self.last_updated_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        lines = []
        for session in sessions:
            active = "active" if session.active else "inactive"
            model = session.model.name if session.model else "unknown"
            context_text = ""
            metrics = session.context_metrics
            if metrics is not None and metrics.source != "unavailable" and metrics.used_tokens is not None:
                if metrics.limit_tokens:
                    percentage = f"{metrics.percentage:.1f}%" if metrics.percentage is not None else "n/a"
                    context_text = f" | ctx={metrics.used_tokens}/{metrics.limit_tokens} ({percentage})"
                else:
                    context_text = f" | ctx={metrics.used_tokens}"
            lines.append(
                f"{session.id} | {session.title} | {model} | "
                f"in={session.tokens.input} out={session.tokens.output} "
                f"cache={session.tokens.cache_read} | {active}{context_text}"
            )
        self.output.setPlainText("\\n".join(lines))
        self._populate_instance_combo()
        self._populate_session_combo()
        self._refresh_interval = self.config_service.settings.refresh_interval_seconds * 1000
        self._timer.setInterval(self._refresh_interval)
        self.config_service.repository.save_sessions(sessions, is_historical=False)
        self.config_service.settings.selected_session = sessions[0].id if sessions else None
        selected_id = self.config_service.settings.selected_session
        selected_session = next((item for item in sessions if item.id == selected_id), None)
        if selected_session is not None:
            self.metric_history.add(sample_from_session(selected_session))
        self.footer_label.setText("Connected to OpenCode.")

    def _populate_session_combo(self) -> None:
        self.session_combo.blockSignals(True)
        self.session_combo.clear()
        for session in self.sessions:
            label = session.title or session.id
            self.session_combo.addItem(label, session.id)
        self.session_combo.setEnabled(bool(self.sessions))

        selected = self.config_service.settings.selected_session
        index = -1
        if selected is not None:
            for i in range(self.session_combo.count()):
                if self.session_combo.itemData(i) == selected:
                    index = i
                    break
        if index < 0 and self.session_combo.count():
            index = 0
        if index >= 0:
            self.session_combo.setCurrentIndex(index)
        self.session_combo.blockSignals(False)
        self._update_selected_details()

    def _populate_instance_combo(self) -> None:
        self.instance_combo.blockSignals(True)
        self.instance_combo.clear()
        for instance in self.instances:
            label = instance.id
            self.instance_combo.addItem(label, instance.id)
        self.instance_combo.setEnabled(bool(self.instances))

        selected = self.config_service.settings.selected_instance
        index = -1
        if selected is not None:
            for i in range(self.instance_combo.count()):
                if self.instance_combo.itemData(i) == selected:
                    index = i
                    break
        if index < 0 and self.instance_combo.count():
            index = 0
        if index >= 0:
            self.instance_combo.setCurrentIndex(index)
        self.instance_combo.blockSignals(False)

    def _on_instance_selected(self, index: int) -> None:
        if index < 0:
            return
        instance_id = self.instance_combo.itemData(index)
        self.config_service.settings.selected_instance = instance_id
        self.config_service.save_settings()
        self._refresh()

    def _on_session_selected(self, index: int) -> None:
        if index < 0:
            return
        session_id = self.session_combo.itemData(index)
        self.config_service.settings.selected_session = session_id
        self.config_service.save_settings()
        self._update_selected_details()

    def _update_selected_details(self) -> None:
        session_id = self.session_combo.currentData()
        session = next((item for item in self.sessions if item.id == session_id), None)
        if session is None:
            self.details_label.setText("No session selected")
            self._clear_charts()
            return
        model = session.model.name if session.model else "unknown"
        active = "active" if session.active else "inactive"
        context_text = ""
        metrics = session.context_metrics
        if metrics is not None and metrics.source != "unavailable" and metrics.used_tokens is not None:
            if metrics.limit_tokens:
                percentage = f"{metrics.percentage:.1f}%" if metrics.percentage is not None else "n/a"
                context_text = f", context={metrics.used_tokens}/{metrics.limit_tokens} ({percentage})"
            else:
                context_text = f", context={metrics.used_tokens}"
        self.details_label.setText(
            f"Selected: {session.id} | {session.title} | {model} | "
            f"in={session.tokens.input} out={session.tokens.output} "
            f"cache={session.tokens.cache_read} | {active}{context_text}"
        )
        self._update_charts(session)

    def _save_config(self) -> None:
        url = self.url_edit.text().strip()
        password = self.password_edit.text().strip() or None
        interval = self.interval_spin.value()
        if not url:
            self.footer_label.setText("URL is required.")
            return
        try:
            from devpulse.integrations.opencode.client import OpenCodeClient

            OpenCodeClient(url)
        except Exception as exc:
            self.footer_label.setText(f"Invalid URL: {exc}")
            return

        authorize_logs = self.sensitive_logs_checkbox.isChecked()
        pin_hash = self.config_service.settings.sensitive_log_pin_hash
        if authorize_logs and not pin_hash:
            pin, accepted = QInputDialog.getText(
                self,
                "Sensitive logs authorization",
                "Enter a PIN to authorize sensitive logs:",
                QLineEdit.Password,
            )
            if not accepted or not pin:
                authorize_logs = False
                self.sensitive_logs_checkbox.setChecked(False)
            else:
                from devpulse.privacy import hash_pin

                pin_hash = hash_pin(pin)

        self.config_service.set_opencode_config(url, password)
        self.config_service.settings.refresh_interval_seconds = interval
        self.config_service.settings.data_source = self.data_source_combo.currentText()
        self.config_service.settings.cache_sensitive_data = self.cache_sensitive_checkbox.isChecked()
        self.config_service.settings.sensitive_logs_authorized = authorize_logs
        self.config_service.settings.sensitive_log_pin_hash = pin_hash if authorize_logs else None
        self.config_service.save_settings()
        self._refresh_interval = interval * 1000
        self._timer.setInterval(self._refresh_interval)
        self.password_edit.clear()
        self.footer_label.setText("Configuration saved. Password is kept in memory for this session only.")
        self._refresh()

    def _prompt_password_once(self) -> None:
        self._password_prompted = True
        password, accepted = QInputDialog.getText(
            self,
            "OpenCode authentication",
            "Password required. Enter it for this session:",
            QLineEdit.Password,
        )
        if accepted and password:
            self.config_service.password = password
            self.footer_label.setText("Password received for this session. It is not stored in plain text.")
            self._refresh()
        else:
            self.footer_label.setText("Password not provided. You can enter it in the Configuration tab.")

    def _is_auth_error(self, error: object) -> bool:
        text = str(error).lower()
        return "401" in text or "unauthorized" in text or "forbidden" in text or "403" in text

    def _toggle_mode(self) -> None:
        settings = self.config_service.settings
        settings.compact_mode = not settings.compact_mode
        self.config_service.save_settings()
        self._apply_mode()
        session = next((item for item in self.sessions if item.id == self.session_combo.currentData()), None)
        if session is not None:
            self._update_charts(session)
        if settings.compact_mode:
            self.footer_label.setText("Compact mode enabled.")
        else:
            self.footer_label.setText("Expanded mode enabled.")

    def _apply_mode(self) -> None:
        compact = self.config_service.settings.compact_mode
        self.compact_chart_view.setVisible(compact)
        self.context_pie_view.setVisible(not compact)
        self.token_chart_view.setVisible(not compact)
        self.trend_chart_view.setVisible(not compact)
        if compact:
            self.resize(360, 300)
        else:
            self.resize(520, 620)

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#2563eb"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "D")
        painter.end()
        self._tray_icon = QSystemTrayIcon(QIcon(pixmap), self)
        menu = QMenu(self)
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.close)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addAction(quit_action)
        self._tray_icon.setContextMenu(menu)
        self._tray_icon.show()

    def _update_charts(self, session) -> None:
        self._update_token_chart(session)
        self._update_compact_chart(session)
        self._update_context_pie(session)
        self._update_trend_chart(session)

    def _update_token_chart(self, session) -> None:
        self.token_chart_view.clear()
        categories, values = token_bar_values(session)
        x = list(range(len(values)))
        bar = pg.BarGraphItem(x=x, height=values, width=0.6, brush="#2563eb")
        self.token_chart_view.addItem(bar)
        self.token_chart_view.getAxis("bottom").setTicks([list(enumerate(categories))])
        self.token_chart_view.setTitle("Tokens")
        self.token_chart_view.showGrid(x=True, y=True, alpha=0.3)

    def _update_compact_chart(self, session) -> None:
        used, limit, _percentage = context_values(session)
        self.compact_chart_view.set_values(used, limit)
        self.compact_chart_view.set_title("Context")

    def _update_context_pie(self, session) -> None:
        used, limit, _percentage = context_values(session)
        self.context_pie_view.set_values(used, limit)
        self.context_pie_view.set_title("Context")

    def _update_trend_chart(self, session) -> None:
        self.trend_chart_view.clear()
        points = context_trend_points(self.metric_history.samples(session.id))
        if points:
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            self.trend_chart_view.plot(xs, ys, pen=pg.mkPen("#2563eb", width=2), symbol="o", symbolBrush="#2563eb")
        self.trend_chart_view.setTitle("Context trend (%)")
        self.trend_chart_view.showGrid(x=True, y=True, alpha=0.3)
        self.trend_chart_view.setLabel("left", "Percent")
        self.trend_chart_view.setYRange(0, 100)

    def _clear_charts(self) -> None:
        self.token_chart_view.clear()
        self.trend_chart_view.clear()
        self.compact_chart_view.set_values(None, None)
        self.context_pie_view.set_values(None, None)

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
