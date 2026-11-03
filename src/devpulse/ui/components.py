from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QConicalGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar

from devpulse.ui.theme import COLORS, get_color


class SectionHeader(QWidget):
    def __init__(self, title: str, icon: str = "", parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        if icon:
            try:
                import qtawesome as qta
                icon_label = QLabel()
                icon_label.setPixmap(qta.icon(icon, color=COLORS["violet"]).pixmap(16, 16))
            except Exception:
                icon_label = QLabel(icon)
                icon_label.setStyleSheet(f"color: {COLORS['violet']}; font-size: 16px;")
            layout.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)
        layout.addStretch(1)


class MetricCard(QFrame):
    def __init__(self, title: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setProperty("card", True)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(6)
        if title:
            header = SectionHeader(title)
            self._layout.addWidget(header)

    def content_layout(self) -> QVBoxLayout:
        return self._layout


class ContextProgress(QWidget):
    """Circular progress indicator for context usage."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._value = 0.0
        self._target = 0.0
        self._label = "Contexto"
        self._color = QColor(COLORS["violet"])
        self._bg = QColor(COLORS["bg_elevated"])
        self._text_color = QColor(COLORS["text_primary"])
        self.setMinimumSize(60, 60)

    def set_value(self, value: float | None) -> None:
        self._target = max(0.0, min(100.0, value or 0.0))
        self._animate()
        self.update()

    def set_label(self, label: str) -> None:
        self._label = label
        self.update()

    def set_colors(self, used_color: str, free_color: str, text_color: str) -> None:
        self._color = QColor(used_color)
        self._bg = QColor(free_color)
        self._text_color = QColor(text_color)
        self.update()

    def _animate(self) -> None:
        anim = QPropertyAnimation(self, b"_value")
        anim.setDuration(400)
        anim.setStartValue(self._value)
        anim.setEndValue(self._target)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.valueChanged.connect(lambda v: self._set_value_internal(v))
        anim.start()
        self._anim = anim

    def _set_value_internal(self, v: float) -> None:
        self._value = v
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.fillRect(rect, QColor(COLORS["bg_card"]))

        diameter = min(rect.width(), rect.height()) - 20
        if diameter < 20:
            painter.end()
            return
        pie_rect = QRectF(
            (rect.width() - diameter) / 2,
            (rect.height() - diameter) / 2,
            diameter,
            diameter,
        )

        # Background ring
        pen = QPen(self._bg, 12)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(pie_rect, 0, 360 * 16)

        # Progress arc
        if self._value > 0:
            span = int(360 * 16 * self._value / 100.0)
            pen = QPen(self._color, 12)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawArc(pie_rect, 90 * 16, -span)

        # Center text
        painter.setPen(QPen(self._text_color))
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        text_rect = QRectF(rect.left(), rect.top(), rect.width(), rect.height() - 12)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self._value:.0f}%")

        # Label
        small_font = QFont()
        small_font.setPointSize(8)
        painter.setFont(small_font)
        label_rect = QRectF(rect.left(), rect.bottom() - 16, rect.width(), 16)
        painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignVCenter, self._label)
        painter.end()


class QuotaCard(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("card", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        self.title = QLabel("Cuota de uso")
        self.title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(self.title)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(True)
        layout.addWidget(self.bar)
        self.remaining_label = QLabel("Restante: -")
        self.renewal_label = QLabel("Renovación: -")
        self.status_label = QLabel("Estado: -")
        for lbl in (self.remaining_label, self.renewal_label, self.status_label):
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
            layout.addWidget(lbl)
        layout.addStretch(1)

    def set_remaining(self, percent: int | None) -> None:
        if percent is None:
            self.bar.setValue(0)
            self.remaining_label.setText("Restante: n/a")
            return
        self.bar.setValue(percent)
        self.remaining_label.setText(f"Restante: {percent}%")
        if percent >= 50:
            self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {COLORS['green']}; }}")
        elif percent >= 20:
            self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {COLORS['yellow']}; }}")
        else:
            self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {COLORS['red']}; }}")

    def set_renewal(self, text: str) -> None:
        self.renewal_label.setText(f"Renovación: {text}")

    def set_status(self, text: str) -> None:
        self.status_label.setText(f"Estado: {text}")


class ContextSummary(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.used_label = QLabel("Tokens usados: -")
        self.cap_label = QLabel("Capacidad: -")
        self.rem_label = QLabel("Restantes: -")
        self.avail_label = QLabel("Disponible: -")
        for lbl in (self.used_label, self.cap_label, self.rem_label, self.avail_label):
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            layout.addWidget(lbl)

    def update_values(self, used: int | None, limit: int | None, percentage: float | None) -> None:
        if used is None:
            self.used_label.setText("Tokens usados: n/a")
            self.cap_label.setText("Capacidad: n/a")
            self.rem_label.setText("Restantes: n/a")
            self.avail_label.setText("Disponible: n/a")
            return
        self.used_label.setText(f"Tokens usados: {used:,}")
        if limit:
            self.cap_label.setText(f"Capacidad: {limit:,}")
            self.rem_label.setText(f"Restantes: {max(limit - used, 0):,}")
            if percentage is None:
                self.avail_label.setText("Disponible: n/a")
            else:
                self.avail_label.setText(f"Disponible: {max(0.0, 100.0 - percentage):.1f}%")
        else:
            self.cap_label.setText("Capacidad: n/a")
            self.rem_label.setText("Restantes: n/a")
            self.avail_label.setText("Disponible: n/a")