import webbrowser

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QPoint
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap, QColor, QShortcut, QKeySequence, QGuiApplication
import pyqtgraph as pg
import qtawesome as qta
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QMessageBox,
    QInputDialog,
    QCheckBox,
    QMenu,
    QSystemTrayIcon,
    QFrame,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QToolButton,
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
from devpulse.ui.components import ContextProgress, QuotaCard, ContextSummary, MetricCard, SectionHeader
from devpulse.ui.context_chart import ContextChart
from devpulse.ui.theme import apply_theme, apply_glow, chart_colors
from devpulse.ui.worker import RefreshWorker


class CardFrame(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("card", True)


class MainWindow(QWidget):
    TIME_FILTERS = {"1h": 3600, "6h": 21600, "24h": 86400, "7d": 604800, "30d": 2592000}

    def __init__(self, config_service: ConfigService) -> None:
        super().__init__()
        self.config_service = config_service
        settings = config_service.settings

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(settings.window_width, settings.window_height)
        if settings.window_x is not None and settings.window_y is not None:
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                geom = screen.availableGeometry()
                x = max(geom.left(), min(settings.window_x, geom.right() - self.width() + 1))
                y = max(geom.top(), min(settings.window_y, geom.bottom() - self.height() + 1))
                self.move(x, y)
            else:
                self.move(settings.window_x, settings.window_y)

        self.sessions = []
        self.instances = []
        self.metric_history = MetricHistory()
        self._password_prompted = False
        self._dragging = False
        self._drag_offset = QPoint()
        self._quitting = False
        self._controls_visible = False
        self.service_usage = None
        self._usage_url = None
        self._time_filter = "24h"

        # Hover timer
        self._hover_timer = QTimer(self)
        self._hover_timer.setInterval(120)
        self._hover_timer.timeout.connect(self._update_controls_visibility)
        self._hover_timer.start()

        # --- Compact widget ---
        self.compact_widget = QWidget()
        self.compact_widget.setMinimumSize(170, 210)
        compact_layout = QVBoxLayout(self.compact_widget)
        compact_layout.setContentsMargins(8, 8, 8, 8)
        compact_layout.setSpacing(20)
        compact_layout.setAlignment(Qt.AlignCenter)
        self.compact_chart_view = PieChartWidget()
        self.compact_chart_view.setMinimumSize(120, 120)
        self.compact_chart_view.setMaximumSize(120, 120)
        self.compact_chart_view.set_title("")
        compact_layout.addWidget(self.compact_chart_view, 0, Qt.AlignCenter)
        self.compact_quota_bar = QProgressBar()
        self.compact_quota_bar.setRange(0, 100)
        self.compact_quota_bar.setValue(0)
        self.compact_quota_bar.setTextVisible(False)
        self.compact_quota_bar.setFixedHeight(8)
        self.compact_quota_bar.setFixedWidth(120)
        compact_layout.addWidget(self.compact_quota_bar, 0, Qt.AlignCenter)
        self.compact_quota_label = QLabel("Cuota de uso: 0%")
        self.compact_quota_label.setStyleSheet("font-size: 10px; color: #A5B0C5;")
        self.compact_quota_label.setVisible(True)
        compact_layout.addWidget(self.compact_quota_label, 0, Qt.AlignCenter)
        self.compact_status = QLabel("●")
        self.compact_status.setStyleSheet("color: #22C55E; font-size: 12px;")
        compact_layout.addWidget(self.compact_status, 0, Qt.AlignCenter)
        # Keep legacy labels hidden for compatibility with existing update calls
        self.compact_icon = QLabel()
        self.compact_tool = QLabel()
        self.compact_model = QLabel()
        self.compact_context_label = QLabel()
        for w in (self.compact_icon, self.compact_tool, self.compact_model, self.compact_context_label):
            w.setVisible(False)

        # Compact hover controls (overlay)
        self.compact_controls = QWidget(self.compact_widget)
        compact_controls_layout = QHBoxLayout(self.compact_controls)
        compact_controls_layout.setContentsMargins(6, 4, 6, 4)
        compact_controls_layout.setSpacing(4)
        self.compact_mode_btn = QPushButton()
        self.compact_mode_btn.setIcon(qta.icon("fa5s.expand-arrows-alt", color="#A855F7"))
        self.compact_mode_btn.setToolTip("Modo")
        self.compact_mode_btn.clicked.connect(self._toggle_mode)
        self.compact_config_btn = QPushButton()
        self.compact_config_btn.setIcon(qta.icon("fa5s.cog", color="#A855F7"))
        self.compact_config_btn.setToolTip("Configuración")
        self.compact_config_btn.clicked.connect(self._open_config_dialog)
        self.compact_refresh_btn = QPushButton()
        self.compact_refresh_btn.setIcon(qta.icon("fa5s.sync", color="#A855F7"))
        self.compact_refresh_btn.setToolTip("Actualizar")
        self.compact_refresh_btn.clicked.connect(self._refresh)
        for btn in (self.compact_mode_btn, self.compact_config_btn, self.compact_refresh_btn):
            btn.setFixedSize(28, 28)
            compact_controls_layout.addWidget(btn)
        self.compact_controls.setVisible(False)
        self.compact_controls.raise_()

        # --- Top bar (expanded) ---
        self.top_bar = CardFrame()
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(10, 6, 10, 6)
        top_layout.setSpacing(8)
        self.app_icon = QLabel()
        self.app_icon.setPixmap(qta.icon("fa5s.code", color="#A855F7").pixmap(24, 24))
        top_layout.addWidget(self.app_icon)
        self.tool_icon = QLabel()
        self.tool_icon.setPixmap(qta.icon("fa5s.terminal", color="#A855F7").pixmap(16, 16))
        top_layout.addWidget(self.tool_icon)
        self.tool_label = QLabel("OpenCode")
        self.tool_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_layout.addWidget(self.tool_label)
        self.model_icon = QLabel()
        self.model_icon.setPixmap(qta.icon("fa5s.microchip", color="#A5B0C5").pixmap(14, 14))
        top_layout.addWidget(self.model_icon)
        self.model_label = QLabel("-")
        top_layout.addWidget(self.model_label)
        self.session_status_label = QLabel("Session: -")
        self.session_status_label.setStyleSheet("color: #22C55E;")
        top_layout.addWidget(self.session_status_label)
        self.last_updated_icon = QLabel()
        self.last_updated_icon.setPixmap(qta.icon("fa5s.clock", color="#A5B0C5").pixmap(14, 14))
        top_layout.addWidget(self.last_updated_icon)
        self.last_updated_label = QLabel("Última actualización: nunca")
        top_layout.addWidget(self.last_updated_label)
        top_layout.addStretch(1)

        # Controls container (hover)
        self.controls_container = QWidget()
        controls_layout = QHBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(4)
        self.instance_combo = QComboBox()
        self.instance_combo.setEnabled(False)
        self.session_combo = QComboBox()
        self.session_combo.setEnabled(False)
        self.refresh_button = QPushButton("Actualizar")
        self.refresh_button.setIcon(qta.icon("fa5s.sync", color="#A855F7"))
        self.mode_button = QPushButton("Modo")
        self.mode_button.setIcon(qta.icon("fa5s.expand-arrows-alt", color="#A855F7"))
        self.config_button = QPushButton("Configuración")
        self.config_button.setIcon(qta.icon("fa5s.cog", color="#A855F7"))
        self.console_button = QPushButton("Consola")
        self.console_button.setIcon(qta.icon("fa5s.external-link-alt", color="#A855F7"))
        self.token_mode_combo = QComboBox()
        self.token_mode_combo.addItems(["Por muestra", "Acumulado"])
        for w in (self.instance_combo, self.session_combo, self.refresh_button, self.mode_button, self.config_button, self.console_button, self.token_mode_combo):
            controls_layout.addWidget(w)
        self.controls_container.setVisible(False)
        top_layout.addWidget(self.controls_container)

        # --- Scrollable content (expanded) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(12)

        # Main metrics row
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(12)

        # Context card
        self.context_card = CardFrame()
        context_layout = QHBoxLayout(self.context_card)
        context_layout.setContentsMargins(12, 12, 12, 12)
        context_layout.setSpacing(12)
        self.context_ring = ContextProgress()
        self.context_ring.setMinimumSize(160, 160)
        self.context_ring.setMaximumSize(160, 160)
        context_layout.addWidget(self.context_ring)
        context_info = QVBoxLayout()
        context_info.setSpacing(4)
        self.context_pct_label = QLabel("Contexto: -")
        self.context_pct_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        context_info.addWidget(self.context_pct_label)
        self.context_summary = ContextSummary()
        context_info.addWidget(self.context_summary)
        context_info.addStretch(1)
        context_layout.addLayout(context_info, 1)
        metrics_row.addWidget(self.context_card, 1)

        self.quota_card = QuotaCard()
        self.quota_open_btn = QPushButton("Abrir cuota")
        self.quota_card.layout().addWidget(self.quota_open_btn)
        metrics_row.addWidget(self.quota_card, 1)

        self.content_layout.addLayout(metrics_row)

        # Charts card
        self.charts_card = CardFrame()
        charts_layout = QVBoxLayout(self.charts_card)
        charts_layout.setContentsMargins(12, 12, 12, 12)
        charts_layout.setSpacing(8)
        charts_header = QHBoxLayout()
        self.charts_title = QLabel("Evolución del uso de contexto")
        self.charts_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        charts_header.addWidget(self.charts_title)
        charts_header.addStretch(1)
        self.time_filter_combo = QComboBox()
        self.time_filter_combo.addItems(["1h", "6h", "24h", "7d", "30d"])
        self.time_filter_combo.setCurrentText("24h")
        charts_header.addWidget(self.time_filter_combo)
        charts_layout.addLayout(charts_header)
        self.trend_chart_view = ContextChart()
        self.trend_chart_view.setMinimumHeight(180)
        charts_layout.addWidget(self.trend_chart_view)
        self.token_trend_chart_view = pg.PlotWidget()
        self.token_trend_chart_view.setMinimumHeight(180)
        self.token_trend_chart_view.setMouseEnabled(x=False, y=False)
        self.token_trend_chart_view.setMenuEnabled(False)
        charts_layout.addWidget(self.token_trend_chart_view)
        self.trend_status_label = QLabel("")
        self.trend_status_label.setWordWrap(True)
        charts_layout.addWidget(self.trend_status_label)
        self.content_layout.addWidget(self.charts_card)
        self.charts_card.setVisible(False)

        # Secondary cards row
        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(12)

        self.tokens_card = CardFrame()
        tokens_layout = QVBoxLayout(self.tokens_card)
        tokens_layout.setContentsMargins(12, 12, 12, 12)
        tokens_layout.setSpacing(4)
        tokens_layout.addWidget(SectionHeader("Tokens por tipo", "fa5s.coins"))
        self.tokens_in_label = QLabel("Entrada: -")
        self.tokens_out_label = QLabel("Salida: -")
        self.tokens_cache_label = QLabel("Caché: -")
        self.tokens_reasoning_label = QLabel("Razonamiento: -")
        for lbl in (self.tokens_in_label, self.tokens_out_label, self.tokens_cache_label, self.tokens_reasoning_label):
            tokens_layout.addWidget(lbl)
        tokens_layout.addStretch(1)
        secondary_row.addWidget(self.tokens_card, 1)

        self.session_card = CardFrame()
        session_layout = QVBoxLayout(self.session_card)
        session_layout.setContentsMargins(12, 12, 12, 12)
        session_layout.setSpacing(4)
        session_layout.addWidget(SectionHeader("Sesión actual", "fa5s.user"))
        self.session_count_label = QLabel("Sesiones activas: -")
        self.session_duration_label = QLabel("Duración: -")
        self.session_messages_label = QLabel("Mensajes: -")
        self.session_last_activity_label = QLabel("Última actividad: -")
        for lbl in (self.session_count_label, self.session_duration_label, self.session_messages_label, self.session_last_activity_label):
            session_layout.addWidget(lbl)
        session_layout.addStretch(1)
        secondary_row.addWidget(self.session_card, 1)

        self.project_card = CardFrame()
        project_layout = QVBoxLayout(self.project_card)
        project_layout.setContentsMargins(12, 12, 12, 12)
        project_layout.setSpacing(4)
        project_layout.addWidget(SectionHeader("Proyecto actual", "fa5s.folder"))
        self.project_name_label = QLabel("Proyecto: -")
        self.project_dir_label = QLabel("Directorio: -")
        self.project_branch_label = QLabel("Rama Git: no disponible")
        self.project_status_label = QLabel("Estado repo: no disponible")
        for lbl in (self.project_name_label, self.project_dir_label, self.project_branch_label, self.project_status_label):
            project_layout.addWidget(lbl)
        project_layout.addStretch(1)
        secondary_row.addWidget(self.project_card, 1)

        self.content_layout.addLayout(secondary_row)

        # Recommendations card
        self.rec_card = CardFrame()
        rec_layout = QVBoxLayout(self.rec_card)
        rec_layout.setContentsMargins(12, 12, 12, 12)
        rec_layout.setSpacing(4)
        rec_layout.addWidget(SectionHeader("Recomendaciones", "fa5s.lightbulb"))
        self.rec_label = QLabel("Sin recomendaciones por el momento.")
        self.rec_label.setWordWrap(True)
        rec_layout.addWidget(self.rec_label)
        self.content_layout.addWidget(self.rec_card)

        # Technical details
        self.tech_card = CardFrame()
        tech_layout = QVBoxLayout(self.tech_card)
        tech_layout.setContentsMargins(12, 12, 12, 12)
        tech_layout.setSpacing(6)
        self.tech_toggle = QToolButton()
        self.tech_toggle.setText("Detalles técnicos")
        self.tech_toggle.setCheckable(True)
        self.tech_toggle.setChecked(False)
        tech_layout.addWidget(self.tech_toggle)
        self.tech_details = QWidget()
        tech_details_layout = QVBoxLayout(self.tech_details)
        tech_details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_label = QLabel("No session selected")
        self.details_label.setWordWrap(True)
        tech_details_layout.addWidget(self.details_label)
        self.token_stats_label = QLabel("Tokens: -")
        self.token_stats_label.setWordWrap(True)
        tech_details_layout.addWidget(self.token_stats_label)
        self.cost_label = QLabel("Cost: -")
        tech_details_layout.addWidget(self.cost_label)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(80)
        tech_details_layout.addWidget(self.output)
        self.tech_details.setVisible(False)
        tech_layout.addWidget(self.tech_details)
        self.content_layout.addWidget(self.tech_card)

        self.scroll_area.setWidget(self.content_widget)

        # --- Root layout ---
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self.scroll_area.setVisible(True)
        self.root_layout.addWidget(self.compact_widget)
        self.root_layout.addWidget(self.top_bar)
        self.root_layout.addWidget(self.scroll_area, 1)
        self.footer_label = QLabel("")
        self.footer_label.setWordWrap(True)
        self.footer_label.setVisible(False)
        self.root_layout.addWidget(self.footer_label)

        # Connections
        self.refresh_button.clicked.connect(self._refresh)
        self.mode_button.clicked.connect(self._toggle_mode)
        self.instance_combo.currentIndexChanged.connect(self._on_instance_selected)
        self.session_combo.currentIndexChanged.connect(self._on_session_selected)
        self.config_button.clicked.connect(self._open_config_dialog)
        self.console_button.clicked.connect(self._open_console)
        self.token_mode_combo.currentIndexChanged.connect(self._on_token_mode_changed)
        self.time_filter_combo.currentIndexChanged.connect(self._on_time_filter_changed)
        self.quota_open_btn.clicked.connect(self._open_usage_page)
        self.tech_toggle.toggled.connect(self.tech_details.setVisible)
        self.quota_page_btn = self.quota_open_btn
        self.usage_page_button = self.quota_open_btn

        self.worker: RefreshWorker | None = None
        self._refresh_interval = settings.refresh_interval_seconds * 1000
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_if_idle)
        self._timer.start(self._refresh_interval)

        self._load_cached_data()
        self._confirm_detected_config()
        self._apply_mode()
        self._apply_chart_theme()
        self._apply_glow_effects()
        self._setup_shortcuts()
        self._setup_tray()

        # Compact pie colors
        self.compact_chart_view.set_colors("#A855F7", "#1B223A", "#F8FAFC")

    def _set_connection_status(self, state: str) -> None:
        mapping = {
            "connected": ("fa5s.check-circle", "Conectado", "#22C55E"),
            "disconnected": ("fa5s.times-circle", "Desconectado", "#EF4444"),
            "reconnecting": ("fa5s.sync", "Reconectando...", "#FACC15"),
            "error": ("fa5s.exclamation-triangle", "Error", "#EF4444"),
        }
        icon_name, text, color = mapping.get(state, ("fa5s.question-circle", state, "#A5B0C5"))
        self.session_status_label.setText(text)
        self.session_status_label.setStyleSheet(f"color: {color}; font-weight: 600;")
        try:
            self.session_status_label.setPixmap(qta.icon(icon_name, color=color).pixmap(14, 14))
        except Exception:
            pass

    # --- Hover ---
    def _update_controls_visibility(self) -> None:
        compact = self.config_service.settings.compact_mode
        # Keep controls visible while interacting with combos or popups
        interacting = False
        if not compact:
            interacting = (
                self.instance_combo.hasFocus()
                or self.session_combo.hasFocus()
                or (self.instance_combo.view() is not None and self.instance_combo.view().isVisible())
                or (self.session_combo.view() is not None and self.session_combo.view().isVisible())
                or QApplication.activePopupWidget() is not None
            )
        visible = self.underMouse() or interacting
        if visible != self._controls_visible:
            self._controls_visible = visible
            if compact:
                self.compact_controls.setVisible(visible)
                if visible:
                    self._position_compact_controls()
            else:
                self.controls_container.setVisible(visible)

    def _position_compact_controls(self) -> None:
        if not hasattr(self, "compact_controls"):
            return
        cw = self.compact_widget
        oc = self.compact_controls
        oc.adjustSize()
        x = max(0, cw.width() - oc.width() - 6)
        y = max(0, cw.height() - oc.height() - 6)
        oc.move(x, y)
        oc.raise_()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if getattr(self, "compact_controls", None) is not None and self.compact_controls.isVisible():
            self._position_compact_controls()

    # --- Dragging ---
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.position().toPoint())
            interactive = (QPushButton, QComboBox, QLineEdit, QSpinBox, QCheckBox, QPlainTextEdit, QDialog, QToolButton, QProgressBar)
            if not isinstance(child, interactive):
                self._dragging = True
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_offset
            screen = QGuiApplication.screenAt(new_pos) or QGuiApplication.primaryScreen()
            if screen is not None:
                geom = screen.availableGeometry()
                x = max(geom.left(), min(new_pos.x(), geom.right() - self.width() + 1))
                y = max(geom.top(), min(new_pos.y(), geom.bottom() - self.height() + 1))
                self.move(x, y)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = False
        super().mouseReleaseEvent(event)

    def enterEvent(self, event) -> None:
        self._update_controls_visibility()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._update_controls_visibility()
        super().leaveEvent(event)

    # --- Config dialog (unchanged logic) ---
    def _open_config_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuration")
        dialog.resize(360, 420)
        layout = QVBoxLayout(dialog)
        header = QLabel()
        header.setPixmap(qta.icon("fa5s.cog", color="#A855F7").pixmap(20, 20))
        layout.addWidget(header)
        form = QFormLayout()
        url_edit = QLineEdit(self.config_service.opencode_url())
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        password_edit.setPlaceholderText("Leave empty to use automatic authentication")
        interval_spin = QSpinBox()
        interval_spin.setMinimum(1)
        interval_spin.setMaximum(300)
        interval_spin.setValue(self.config_service.settings.refresh_interval_seconds)
        cache_sensitive_checkbox = QCheckBox("Cache sensitive data in memory")
        cache_sensitive_checkbox.setChecked(self.config_service.settings.cache_sensitive_data)
        sensitive_logs_checkbox = QCheckBox("Authorize sensitive logs")
        sensitive_logs_checkbox.setChecked(self.config_service.settings.sensitive_logs_authorized)
        data_source_combo = QComboBox()
        data_source_combo.addItems(["auto", "http", "cli"])
        data_source_combo.setCurrentText(self.config_service.settings.data_source)
        theme_combo = QComboBox()
        theme_combo.addItems(["classic", "neon"])
        theme_combo.setCurrentText(self.config_service.settings.theme_mode)
        accent_combo = QComboBox()
        accent_combo.addItem("Magenta", "#ff00ff")
        accent_combo.addItem("Cyan", "#00f5ff")
        accent_combo.addItem("Green", "#39ff14")
        idx = accent_combo.findData(self.config_service.settings.accent_color)
        if idx >= 0:
            accent_combo.setCurrentIndex(idx)
        glow_combo = QComboBox()
        glow_combo.addItems(["subtle", "medium", "strong"])
        glow_combo.setCurrentText(self.config_service.settings.glow_strength)
        font_combo = QComboBox()
        font_combo.addItems(["small", "medium", "large"])
        font_combo.setCurrentText(self.config_service.settings.font_size)
        reduce_motion_checkbox = QCheckBox("Reduce motion")
        reduce_motion_checkbox.setChecked(self.config_service.settings.reduce_motion)

        form.addRow("OpenCode URL", url_edit)
        form.addRow("Password (optional)", password_edit)
        form.addRow("Refresh interval (s)", interval_spin)
        form.addRow(cache_sensitive_checkbox)
        form.addRow(sensitive_logs_checkbox)
        form.addRow("Data source", data_source_combo)
        form.addRow("Theme", theme_combo)
        form.addRow("Accent color", accent_combo)
        form.addRow("Glow strength", glow_combo)
        form.addRow("Font size", font_combo)
        form.addRow(reduce_motion_checkbox)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        for btn in buttons.buttons():
            if btn.text().lower().startswith("save"):
                btn.setIcon(qta.icon("fa5s.save", color="#A855F7"))
            elif btn.text().lower().startswith("cancel"):
                btn.setIcon(qta.icon("fa5s.times", color="#A855F7"))
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        url = url_edit.text().strip()
        password = password_edit.text().strip() or None
        interval = interval_spin.value()
        if not url:
            return
        try:
            from devpulse.integrations.opencode.client import OpenCodeClient

            OpenCodeClient(url)
        except Exception:
            return

        authorize_logs = sensitive_logs_checkbox.isChecked()
        pin_hash = self.config_service.settings.sensitive_log_pin_hash
        if authorize_logs and not pin_hash:
            pin, accepted = QInputDialog.getText(
                self, "Sensitive logs authorization", "Enter a PIN to authorize sensitive logs:", QLineEdit.Password
            )
            if not accepted or not pin:
                authorize_logs = False
            else:
                from devpulse.privacy import hash_pin

                pin_hash = hash_pin(pin)

        self.config_service.set_opencode_config(url, password)
        self.config_service.settings.refresh_interval_seconds = interval
        self.config_service.settings.data_source = data_source_combo.currentText()
        self.config_service.settings.cache_sensitive_data = cache_sensitive_checkbox.isChecked()
        self.config_service.settings.sensitive_logs_authorized = authorize_logs
        self.config_service.settings.sensitive_log_pin_hash = pin_hash if authorize_logs else None
        self.config_service.settings.theme_mode = theme_combo.currentText()
        self.config_service.settings.accent_color = accent_combo.currentData()
        self.config_service.settings.glow_strength = glow_combo.currentText()
        self.config_service.settings.font_size = font_combo.currentText()
        self.config_service.settings.reduce_motion = reduce_motion_checkbox.isChecked()
        self.config_service.save_settings()
        apply_theme(QApplication.instance(), self.config_service.settings)
        self._apply_chart_theme()
        self._apply_glow_effects()
        self._refresh_interval = interval * 1000
        self._timer.setInterval(self._refresh_interval)
        self._refresh()

    def _confirm_detected_config(self) -> None:
        source = self.config_service.config_source
        url = self.config_service.opencode_url()
        if source in {"environment", "service.json"}:
            answer = QMessageBox.question(
                self, "OpenCode configuration detected",
                f"Use automatically detected configuration?\n\nURL: {url}\nSource: {source}",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
            )
            if answer == QMessageBox.No:
                pass
        else:
            pass

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
            self.status_label if hasattr(self, "status_label") else None
            return
        if hasattr(self, "status_label"):
            self.status_label.setText("Status: connecting...")
        self.refresh_button.setEnabled(False)
        self._set_connection_status("reconnecting")
        url = self.config_service.opencode_url()
        password = self.config_service.password
        self.worker = RefreshWorker(
            url, password,
            self.config_service.settings.selected_instance,
            self.config_service.settings.data_source,
        )
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, instances, sessions, selected_instance_id, error, usage) -> None:
        self.refresh_button.setEnabled(True)
        self.service_usage = usage
        if error:
            self.config_service.retry_policy.record_failure()
            if self.config_service.retry_policy.blocked:
                self._timer.stop()
            self._refresh_interval = min(self._refresh_interval * 2, 60000)
            self._timer.setInterval(self._refresh_interval)
            if hasattr(self, "status_label"):
                self.status_label.setText("Status: error")
            cached = self.config_service.repository.load_latest()
            if cached:
                self.config_service.repository.mark_historical()
                if hasattr(self, "status_label"):
                    self.status_label.setText("Status: using cached data")
                lines = [f"{row['session_id']} | {row['title']} (historical)" for row in cached]
                self.output.setPlainText("\n".join(lines))
            else:
                self.output.setPlainText(str(error))
            if self._is_auth_error(error) and not self._password_prompted:
                self._prompt_password_once()
            self._set_connection_status("error")
            self._update_service_usage()
            return

        from datetime import datetime

        self.sessions = sessions
        self.instances = instances
        if selected_instance_id is not None:
            self.config_service.settings.selected_instance = selected_instance_id
        self.config_service.retry_policy.record_success()
        if hasattr(self, "status_label"):
            self.status_label.setText(f"Status: connected ({len(sessions)} sessions)")
        self.last_updated_label.setText(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
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
        self.output.setPlainText("\n".join(lines))
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
        self._update_selected_details()
        if any(getattr(instance, "id", "") == "opencode-cli" for instance in instances):
            self.footer_label.setText("Connected via CLI. Context % may be unavailable if model limits cannot be resolved.")
        else:
            self.footer_label.setText("Connected to OpenCode.")
        self._set_connection_status("connected")
        self._update_service_usage()
        self._update_recommendations()

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
            self._update_secondary_cards(None)
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
        self._update_secondary_cards(session)
        self._update_context_card(session)

    def _update_context_card(self, session) -> None:
        used, limit, percentage = context_values(session)
        if used is None:
            self.context_pct_label.setText("Contexto: n/a")
            self.context_summary.update_values(None, None, None)
            self.context_ring.set_value(None)
            return
        pct_text = f"{percentage:.1f}%" if percentage is not None else "n/a"
        self.context_pct_label.setText(f"Contexto: {pct_text}")
        self.context_summary.update_values(used, limit, percentage)
        self.context_ring.set_value(percentage if percentage is not None else 0.0)
        self.context_ring.set_label("Contexto utilizado")
        colors = chart_colors(self.config_service.settings)
        self.context_ring.set_colors(colors["used"], colors["free"], colors["text"])

    def _update_secondary_cards(self, session) -> None:
        if session is None:
            self.tokens_in_label.setText("Entrada: -")
            self.tokens_out_label.setText("Salida: -")
            self.tokens_cache_label.setText("Caché: -")
            self.tokens_reasoning_label.setText("Razonamiento: -")
            self.session_count_label.setText("Sesiones activas: -")
            self.session_duration_label.setText("Duración: -")
            self.session_messages_label.setText("Mensajes: -")
            self.session_last_activity_label.setText("Última actividad: -")
            self.project_name_label.setText("Proyecto: -")
            self.project_dir_label.setText("Directorio: -")
            return
        self.tokens_in_label.setText(f"Entrada: {session.tokens.input:,}")
        self.tokens_out_label.setText(f"Salida: {session.tokens.output:,}")
        self.tokens_cache_label.setText(f"Caché: {session.tokens.cache_read:,}")
        self.tokens_reasoning_label.setText(f"Razonamiento: {session.tokens.reasoning:,}")
        active_count = sum(1 for s in self.sessions if s.active)
        self.session_count_label.setText(f"Sesiones activas: {active_count}")
        if session.updated_at:
            from datetime import datetime

            try:
                dt = datetime.fromtimestamp(session.updated_at / 1000) if session.updated_at > 1e12 else datetime.fromtimestamp(session.updated_at)
                self.session_last_activity_label.setText(f"Última actividad: {dt.strftime('%H:%M:%S')}")
            except (ValueError, OSError):
                self.session_last_activity_label.setText("Última actividad: n/a")
        else:
            self.session_last_activity_label.setText("Última actividad: n/a")
        self.session_duration_label.setText("Duración: n/a")
        self.session_messages_label.setText("Mensajes: n/a")
        self.project_name_label.setText(f"Proyecto: {session.project_id or 'n/a'}")
        self.project_dir_label.setText(f"Directorio: {session.directory or 'n/a'}")

    def _update_service_usage(self) -> None:
        usage = getattr(self, "service_usage", None)
        if not isinstance(usage, dict):
            self.quota_card.set_remaining(None)
            self.quota_card.set_renewal("n/a")
            self.quota_card.set_status("No disponible")
            self.compact_quota_label.setText("Cuota de uso: 0%")
            self.compact_quota_bar.setValue(0)
            return
        tokens = usage.get("tokens") or {}
        cache = tokens.get("cache") or {}
        prompts = usage.get("prompts")
        steps = usage.get("steps")
        cost = usage.get("cost")
        parts = []
        if prompts is not None:
            parts.append(f"prompts={prompts}")
        if steps is not None:
            parts.append(f"steps={steps}")
        parts.append(f"tokens in={tokens.get('input', 0)} out={tokens.get('output', 0)}")
        parts.append(f"reasoning={tokens.get('reasoning', 0)} cache={cache.get('read', 0)}")
        if cost is not None:
            parts.append(f"cost={cost}")
        self.token_stats_label.setText(
            f"Tokens: in={tokens.get('input', 0)} out={tokens.get('output', 0)} reasoning={tokens.get('reasoning', 0)} cache={cache.get('read', 0)}"
        )
        self.cost_label.setText(f"Cost: {cost if cost is not None else '-'}")

        limits = usage.get("limits") or {}
        data = limits.get("data", limits) if isinstance(limits, dict) else {}
        if not isinstance(data, dict):
            data = {}
        self._usage_url = data.get("usageURL") or data.get("usage_url")
        go = data.get("go") or {}
        rolling = go.get("rolling") or {}
        weekly = go.get("weekly") or {}
        monthly = go.get("monthly") or {}
        def remaining(item):
            pct = item.get("percent")
            if pct is None:
                return "n/a"
            return f"{max(0, 100 - int(pct))}%"
        def reset_text(item):
            ts = item.get("resetsAt") or item.get("resets_at")
            if not ts:
                return "n/a"
            try:
                from datetime import datetime
                return datetime.fromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d %H:%M")
            except (ValueError, OSError):
                return str(ts)
        limited = go.get("limited") if isinstance(go.get("limited"), bool) else None
        # Update QuotaCard with monthly remaining
        monthly_pct = monthly.get("percent")
        if monthly_pct is None:
            self.quota_card.set_remaining(None)
        else:
            self.quota_card.set_remaining(max(0, 100 - int(monthly_pct)))
        self.quota_card.set_renewal(reset_text(monthly))
        if limited is True:
            self.quota_card.set_status("Limited")
        elif limited is False:
            self.quota_card.set_status("Not limited")
        else:
            self.quota_card.set_status("Unknown")
        mr = remaining(monthly)
        self.compact_quota_label.setText("Quota:")
        monthly_pct = monthly.get("percent")
        if monthly_pct is None:
            self.compact_quota_bar.setValue(0)
            self.compact_quota_label.setText("Cuota de uso: n/a")
        else:
            remaining = max(0, 100 - int(monthly_pct))
            self.compact_quota_bar.setValue(remaining)
            self.compact_quota_label.setText(f"Cuota de uso: {remaining}%")

    def _update_recommendations(self) -> None:
        recs = []
        # Context-based
        session = next((item for item in self.sessions if item.id == self.session_combo.currentData()), None)
        if session is not None:
            metrics = session.context_metrics
            if metrics is not None and metrics.percentage is not None:
                if metrics.percentage >= 85:
                    recs.append("El contexto está llegando al límite. Considerá resumir la conversación.")
                elif metrics.percentage >= 70:
                    recs.append("El contexto está creciendo. Monitoreá el consumo.")
        # Quota-based
        usage = getattr(self, "service_usage", None)
        if isinstance(usage, dict):
            limits = usage.get("limits") or {}
            data = limits.get("data", limits) if isinstance(limits, dict) else {}
            go = data.get("go") if isinstance(data, dict) else None
            if isinstance(go, dict):
                monthly = go.get("monthly") or {}
                pct = monthly.get("percent")
                if pct is not None and int(pct) >= 80:
                    recs.append("La cuota de uso está próxima a agotarse.")
        if not recs:
            recs.append("Sin recomendaciones por el momento.")
        self.rec_label.setText("\n".join(f"• {r}" for r in recs))

    def _update_charts(self, session) -> None:
        self._update_compact_chart(session)
        self._update_context_pie(session)
        self._update_trend_chart(session)
        self._update_token_trend_chart(session)

    def _update_compact_chart(self, session) -> None:
        colors = chart_colors(self.config_service.settings)
        used, limit, _percentage = context_values(session)
        self.compact_chart_view.set_values(used, limit)
        self.compact_chart_view.set_title("")
        self.compact_chart_view.set_colors(colors["used"], colors["free"], colors["text"])
        if _percentage is not None:
            self.compact_context_label.setText(f"{_percentage:.0f}%")
        else:
            self.compact_context_label.setText("n/a")

    def _update_context_pie(self, session) -> None:
        colors = chart_colors(self.config_service.settings)
        used, limit, percentage = context_values(session)
        self.context_pie_view if hasattr(self, "context_pie_view") else None
        # context ring already updated in _update_context_card

    def _update_trend_chart(self, session) -> None:
        colors = chart_colors(self.config_service.settings)
        points = context_trend_points(self.metric_history.samples(session.id))
        window = self.TIME_FILTERS.get(self._time_filter, 86400)
        now = points[-1][0] if points else None
        if now is not None:
            cutoff = now - window
            points = [p for p in points if p[0] >= cutoff]
        if points:
            self.trend_chart_view.plot_data(points, color=colors["primary"])
            ys = [p[1] for p in points]
            if ys:
                self.trend_chart_view.setTitle(f"Evolución del contexto (%) - último: {ys[-1]:.1f}%", color=colors["text"])
            # Fix negative axes
            xs = [p[0] for p in points]
            if xs:
                self.trend_chart_view.setXRange(min(xs), max(xs), padding=0.05)
            if ys:
                self.trend_chart_view.setYRange(0, max(100, max(ys)), padding=0.05)
            self.trend_status_label.setText("")
        else:
            self.trend_chart_view.clear()
            self.trend_chart_view.setBackground(colors["background"])
            self.trend_status_label.setText("No hay suficientes datos para mostrar la evolución del contexto.")
            self.trend_chart_view.setTitle("Evolución del contexto (%)", color=colors["text"])

    def _update_token_trend_chart(self, session) -> None:
        colors = chart_colors(self.config_service.settings)
        self.token_trend_chart_view.clear()
        self.token_trend_chart_view.setBackground(colors["background"])
        samples = self.metric_history.samples(session.id)
        window = self.TIME_FILTERS.get(self._time_filter, 86400)
        if samples:
            now = samples[-1].timestamp
            cutoff = now - window
            samples = [s for s in samples if s.timestamp >= cutoff]
        if not samples:
            self.token_trend_chart_view.setTitle("Tokens (entrada/salida)", color=colors["text"])
            self.token_trend_chart_view.showGrid(x=True, y=True, alpha=0.15)
            return
        first = samples[0].timestamp
        xs = [max(0.0, (s.timestamp - first) / 60.0) for s in samples]
        mode = self.token_mode_combo.currentText()
        if mode == "Acumulado":
            ys_in, ys_out = [], []
            ci, co = 0, 0
            for s in samples:
                ci += s.input_tokens
                co += s.output_tokens
                ys_in.append(ci)
                ys_out.append(co)
        else:
            ys_in = [s.input_tokens for s in samples]
            ys_out = [s.output_tokens for s in samples]

        curve_in = self.token_trend_chart_view.plot(
            xs, ys_in, pen=pg.mkPen(colors["primary"], width=2.5), symbol="o", symbolSize=5,
            symbolBrush=colors["primary"], name="Input",
        )
        curve_out = self.token_trend_chart_view.plot(
            xs, ys_out, pen=pg.mkPen(colors["secondary"], width=2.5), symbol="s", symbolSize=5,
            symbolBrush=colors["secondary"], name="Output",
        )
        base = pg.PlotDataItem(xs, [0.0] * len(xs))
        self.token_trend_chart_view.addItem(pg.FillBetweenItem(curve_in, base, brush=pg.mkBrush(colors["primary"] + "22")))
        base2 = pg.PlotDataItem(xs, [0.0] * len(xs))
        self.token_trend_chart_view.addItem(pg.FillBetweenItem(curve_out, base2, brush=pg.mkBrush(colors["secondary"] + "22")))
        title_suffix = "acumulado" if mode == "Acumulado" else "por muestra"
        self.token_trend_chart_view.setTitle(f"Tokens (entrada/salida) - {title_suffix}", color=colors["text"])
        self.token_trend_chart_view.showGrid(x=True, y=True, alpha=0.15)
        self.token_trend_chart_view.setLabel("left", "Tokens", color=colors["text"])
        self.token_trend_chart_view.setLabel("bottom", "Minutes", color=colors["text"])
        if xs:
            self.token_trend_chart_view.setXRange(0, max(xs) if max(xs) > 0 else 1, padding=0.05)
        all_ys = ys_in + ys_out
        if all_ys:
            self.token_trend_chart_view.setYRange(0, max(all_ys) if max(all_ys) > 0 else 1, padding=0.05)
        for name in ("left", "bottom"):
            self.token_trend_chart_view.getAxis(name).setTextPen(pg.mkPen(colors["text"]))
            self.token_trend_chart_view.getAxis(name).setPen(pg.mkPen(colors["grid"]))
        if self.token_trend_chart_view.getPlotItem().legend is None:
            self.token_trend_chart_view.addLegend(offset=(10, 10))

    def _on_token_mode_changed(self, index: int) -> None:
        session = next((item for item in self.sessions if item.id == self.session_combo.currentData()), None)
        if session is not None:
            self._update_token_trend_chart(session)

    def _on_time_filter_changed(self, index: int) -> None:
        self._time_filter = self.time_filter_combo.currentText()
        session = next((item for item in self.sessions if item.id == self.session_combo.currentData()), None)
        if session is not None:
            self._update_trend_chart(session)
            self._update_token_trend_chart(session)

    def _open_usage_page(self) -> None:
        url = getattr(self, "_usage_url", None) or "https://opencode.ai/console/"
        webbrowser.open(url)

    def _open_console(self) -> None:
        answer = QMessageBox.question(
            self, "OpenCode Console (optional)",
            "Do you want to open the OpenCode console in your browser?\n\n"
            "DevPulse will not store any credentials.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            webbrowser.open("https://opencode.ai/console/")

    def _prompt_password_once(self) -> None:
        self._password_prompted = True
        password, accepted = QInputDialog.getText(
            self, "OpenCode authentication", "Password required. Enter it for this session:", QLineEdit.Password
        )
        if accepted and password:
            self.config_service.password = password
            self._refresh()
        else:
            pass

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
            pass
        else:
            pass

    def _apply_mode(self) -> None:
        compact = self.config_service.settings.compact_mode
        self.compact_widget.setVisible(compact)
        self.top_bar.setVisible(not compact)
        self.scroll_area.setVisible(not compact)
        target = QSize(160, 190) if compact else QSize(720, 520)
        if self.config_service.settings.reduce_motion:
            self.resize(target)
            return
        animation = QPropertyAnimation(self, b"size")
        animation.setDuration(180)
        animation.setStartValue(self.size())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self._mode_animation = animation

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self._tray_icon = QSystemTrayIcon(qta.icon("fa5s.code", color="#A855F7"), self)
        menu = QMenu(self)
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addAction(quit_action)
        self._tray_icon.setContextMenu(menu)
        self._tray_icon.show()

    def _quit_app(self) -> None:
        self._quitting = True
        self.close()

    def _clear_charts(self) -> None:
        self.trend_chart_view.clear()
        self.token_trend_chart_view.clear()
        self.compact_chart_view.set_values(None, None)
        self.context_ring.set_value(None)

    def _apply_chart_theme(self) -> None:
        colors = chart_colors(self.config_service.settings)
        self.trend_chart_view.setBackground(colors["background"])
        self.token_trend_chart_view.setBackground(colors["background"])
        self.compact_chart_view.set_colors(colors["used"], colors["free"], colors["text"])
        self.context_ring.set_colors(colors["used"], colors["free"], colors["text"])

    def _apply_glow_effects(self) -> None:
        settings = self.config_service.settings
        cards = []
        for child in self.findChildren(CardFrame):
            cards.append(child)
        for card in cards:
            apply_glow(card, settings)
        for widget in (self.compact_chart_view, self.context_ring, self.trend_chart_view, self.token_trend_chart_view):
            apply_glow(widget, settings)
        if settings.theme_mode != "neon":
            for button in (self.refresh_button, self.mode_button, self.config_button, self.quota_open_btn, self.usage_page_button, self.console_button):
                button.setGraphicsEffect(None)

    def _setup_shortcuts(self) -> None:
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self._refresh)
        mode_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        mode_shortcut.activated.connect(self._toggle_mode)

    def closeEvent(self, event) -> None:
        if getattr(self, "_tray_icon", None) is not None and not self._quitting:
            self.hide()
            event.ignore()
            return
        settings = self.config_service.settings
        settings.window_width = self.width()
        settings.window_height = self.height()
        settings.window_x = self.x()
        settings.window_y = self.y()
        self._timer.stop()
        self.config_service.save_settings()
        self.config_service.close()
        super().closeEvent(event)