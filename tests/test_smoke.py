from devpulse.ui.main_window import MainWindow
from devpulse.ui.components import (
    ContextProgress,
    QuotaCard,
    ContextSummary,
    MetricCard,
    SectionHeader,
)
from devpulse.ui.theme import COLORS, chart_colors, apply_theme, apply_glow
from devpulse.ui.charts import context_trend_points, context_values, token_bar_values
from devpulse.ui.context_chart import ContextChart
from devpulse.ui.pie_chart import PieChartWidget


def test_import_main_window() -> None:
    assert MainWindow is not None


def test_import_components() -> None:
    assert all(obj is not None for obj in (ContextProgress, QuotaCard, ContextSummary, MetricCard, SectionHeader))


def test_import_theme() -> None:
    assert "violet" in COLORS


def test_import_charts() -> None:
    assert callable(context_values)


def test_import_context_chart() -> None:
    assert ContextChart is not None


def test_import_pie_chart() -> None:
    assert PieChartWidget is not None