from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen
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
        self.setMinimumHeight(120)

    def set_values(self, used: int | None, limit: int | None) -> None:
        self._used = max(used or 0, 0)
        self._limit = max(limit or 0, 0)
        self.update()

    def set_title(self, title: str) -> None:
        self._title = title
        self.update()

    def set_colors(self, used_color: str, free_color: str, text_color: str) -> None:
        self._used_color = QColor(used_color)
        self._free_color = QColor(free_color)
        self._text_color = QColor(text_color)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.fillRect(rect, self.palette().window())

        diameter = min(rect.width(), rect.height()) - 24
        if diameter < 20:
            painter.end()
            return
        pie_rect = QRectF(
            (rect.width() - diameter) / 2,
            (rect.height() - diameter) / 2,
            diameter,
            diameter,
        )

        if self._limit > 0:
            used_angle = int(360 * 16 * self._used / self._limit)
            free_angle = 360 * 16 - used_angle
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._used_color)
            painter.drawPie(pie_rect, 90 * 16, -used_angle)
            painter.setBrush(self._free_color)
            painter.drawPie(pie_rect, 90 * 16 - used_angle, -free_angle)
            percentage = (self._used / self._limit) * 100
            text = f"{percentage:.1f}%"
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._free_color)
            painter.drawPie(pie_rect, 0, 360 * 16)
            text = "n/a"

        painter.setPen(QPen(self._text_color))
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.setPen(QPen(self._text_color))
        small_font = QFont()
        small_font.setPointSize(9)
        painter.setFont(small_font)
        painter.drawText(rect.adjusted(0, diameter // 2 + 18, 0, 0), Qt.AlignHCenter, self._title)
        painter.end()