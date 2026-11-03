from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import pyqtgraph as pg

from devpulse.ui.theme import COLORS


class ContextChart(pg.PlotWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setBackground(COLORS["bg_secondary"])
        self.showGrid(x=True, y=True, alpha=0.15)
        self.setLabel("left", "Percent", color=COLORS["text_secondary"])
        self.setLabel("bottom", "Minutes", color=COLORS["text_secondary"])
        self.setYRange(0, 100)
        self.getAxis("left").setTextPen(pg.mkPen(COLORS["text_secondary"]))
        self.getAxis("bottom").setTextPen(pg.mkPen(COLORS["text_secondary"]))
        self.getPlotItem().legend = None
        self._legend = self.addLegend(offset=(10, 10))
        self.setMouseEnabled(x=False, y=False)
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=False, y=False)
        self.setMenuEnabled(False)

    def plot_data(self, points: list, color: str = COLORS["violet"]) -> None:
        self.clear()
        self.setBackground(COLORS["bg_secondary"])
        self.showGrid(x=True, y=True, alpha=0.15)
        self.setYRange(0, 100)
        if not points:
            self.setTitle("Context trend (%)", color=COLORS["text_secondary"])
            return
        first = points[0][0]
        xs = [max(0.0, (p[0] - first) / 60.0) for p in points]
        ys = [p[1] for p in points]
        pen = pg.mkPen(color, width=2.5)
        curve = self.plot(xs, ys, pen=pen, symbol="o", symbolSize=5, symbolBrush=color, name="Context %")
        baseline = pg.PlotDataItem(xs, [0.0] * len(xs))
        fill = pg.FillBetweenItem(curve, baseline, brush=pg.mkBrush(color + "33"))
        self.addItem(fill)
        if ys:
            self.setTitle(f"Context trend (%) - last: {ys[-1]:.1f}%", color=COLORS["text_secondary"])
        if xs:
            self.setXRange(0, max(xs) if max(xs) > 0 else 1, padding=0.05)