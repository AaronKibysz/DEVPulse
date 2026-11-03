import time

from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient, QConicalGradient
from PySide6.QtWidgets import QWidget


class PieChartWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._used = 0
        self._limit = 0
        self._title = "Context"
        self._used_color = QColor("#2563eb")
        self._free_color = QColor("#94a3b8")
        self._text_color = QColor("#111827")

        # Animated display values
        self._display_used = 0.0
        self._display_limit = 0.0
        self._target_used = 0.0
        self._target_limit = 0.0
        self._anim_from_used = 0.0
        self._anim_from_limit = 0.0
        self._anim_start = 0.0
        self._anim_duration = 260.0
        self._animating = False
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)
        self._anim_timer.timeout.connect(self._step_animation)

        self.setMinimumHeight(100)

    def set_values(self, used: int | None, limit: int | None) -> None:
        self._target_used = float(max(used or 0, 0))
        self._target_limit = float(max(limit or 0, 0))
        self._anim_from_used = self._display_used
        self._anim_from_limit = self._display_limit
        self._anim_start = time.time() * 1000.0
        self._animating = True
        self._anim_timer.start()
        self.update()

    def set_title(self, title: str) -> None:
        self._title = title
        self.update()

    def set_colors(self, used_color: str, free_color: str, text_color: str) -> None:
        self._used_color = QColor(used_color)
        self._free_color = QColor(free_color)
        self._text_color = QColor(text_color)
        self.update()

    def _step_animation(self) -> None:
        now = time.time() * 1000.0
        t = (now - self._anim_start) / self._anim_duration
        if t >= 1.0:
            t = 1.0
            self._animating = False
            self._anim_timer.stop()
        # ease out cubic
        ease = 1.0 - (1.0 - t) ** 3
        self._display_used = self._anim_from_used + (self._target_used - self._anim_from_used) * ease
        self._display_limit = self._anim_from_limit + (self._target_limit - self._anim_from_limit) * ease
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.fillRect(rect, self.palette().window())

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

        used = self._display_used
        limit = self._display_limit

        # Glow for neon: draw a soft outer ring
        glow_color = QColor(self._used_color)
        glow_color.setAlpha(60)
        painter.setPen(QPen(glow_color, 6))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(pie_rect.adjusted(-2, -2, 2, 2))

        if limit > 0:
            used_angle = int(360 * 16 * used / limit)
            free_angle = 360 * 16 - used_angle
            # Used slice with conical gradient
            grad = QConicalGradient(pie_rect.center(), 90)
            grad.setColorAt(0.0, self._used_color)
            grad.setColorAt(1.0, QColor(self._used_color).darker(140))
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawPie(pie_rect, 90 * 16, -used_angle)
            # Free slice
            painter.setBrush(self._free_color)
            painter.drawPie(pie_rect, 90 * 16 - used_angle, -free_angle)
            percentage = (used / limit) * 100 if limit else 0.0
            text = f"{percentage:.1f}%"
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._free_color)
            painter.drawPie(pie_rect, 0, 360 * 16)
            text = "n/a"

        # Inner highlight ring
        inner = pie_rect.adjusted(6, 6, -6, -6)
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(inner)

        painter.setPen(QPen(self._text_color))
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.setPen(QPen(self._text_color))
        small_font = QFont()
        small_font.setPointSize(9)
        painter.setFont(small_font)
        painter.drawText(rect.adjusted(0, diameter // 2 + 16, 0, 0), Qt.AlignHCenter, self._title)
        painter.end()
