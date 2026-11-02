from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect


FONT_SIZES = {"small": 9, "medium": 11, "large": 13}
GLOW_RADII = {"subtle": 8, "medium": 16, "strong": 28}
ACCENT_PRESETS = {
    "magenta": "#ff00ff",
    "cyan": "#00f5ff",
    "green": "#39ff14",
}


def normalize_accent(color: str) -> str:
    color = (color or "#ff00ff").strip()
    if not color.startswith("#"):
        color = ACCENT_PRESETS.get(color.lower(), color)
    if len(color) == 4:
        color = "#" + "".join(part * 2 for part in color[1:])
    return color


def secondary_accent(color: str) -> str:
    color = normalize_accent(color).lower()
    if color == "#ff00ff":
        return "#00f5ff"
    if color == "#00f5ff":
        return "#ff00ff"
    return "#00f5ff"


def classic_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f4f6fb"))
    palette.setColor(QPalette.WindowText, QColor("#111827"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#eef2f7"))
    palette.setColor(QPalette.Text, QColor("#111827"))
    palette.setColor(QPalette.Button, QColor("#e5e7eb"))
    palette.setColor(QPalette.ButtonText, QColor("#111827"))
    palette.setColor(QPalette.Highlight, QColor("#2563eb"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    return palette


def neon_palette(accent: str) -> QPalette:
    accent_color = QColor(normalize_accent(accent))
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#070a14"))
    palette.setColor(QPalette.WindowText, QColor("#f2f5ff"))
    palette.setColor(QPalette.Base, QColor("#050816"))
    palette.setColor(QPalette.AlternateBase, QColor("#0b1020"))
    palette.setColor(QPalette.Text, QColor("#f2f5ff"))
    palette.setColor(QPalette.Button, QColor("#0b1020"))
    palette.setColor(QPalette.ButtonText, accent_color)
    palette.setColor(QPalette.Highlight, accent_color)
    palette.setColor(QPalette.HighlightedText, QColor("#050816"))
    return palette


def chart_colors(settings) -> Dict[str, str]:
    accent = normalize_accent(getattr(settings, "accent_color", "#ff00ff"))
    secondary = secondary_accent(accent)
    if getattr(settings, "theme_mode", "classic") == "neon":
        return {
            "background": "#0b1020",
            "text": "#f2f5ff",
            "grid": accent + "33",
            "primary": accent,
            "secondary": secondary,
            "tertiary": "#39ff14",
            "muted": "#1a1a2e",
            "used": accent,
            "free": "#1a1a2e",
        }
    return {
        "background": "#f8fafc",
        "text": "#111827",
        "grid": "#94a3b833",
        "primary": "#2563eb",
        "secondary": "#94a3b8",
        "tertiary": "#10b981",
        "muted": "#e5e7eb",
        "used": "#2563eb",
        "free": "#94a3b8",
    }


def neon_stylesheet(accent: str, glow_strength: str, font_size: str) -> str:
    accent = normalize_accent(accent)
    secondary = secondary_accent(accent)
    size = FONT_SIZES.get(font_size, 11)
    radius = GLOW_RADII.get(glow_strength, 28)
    return f"""
    QWidget {{
        background-color: #070a14;
        color: #f2f5ff;
        font-size: {size}px;
    }}
    QFrame[card="true"] {{
        background-color: #0b1020;
        border: 1px solid {accent}66;
        border-radius: 12px;
    }}
    QPushButton {{
        background-color: transparent;
        color: {accent};
        border: 1px solid {accent};
        border-radius: 8px;
        padding: 6px 12px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {accent}22;
        color: #ffffff;
    }}
    QPushButton:pressed {{
        background-color: {accent}44;
    }}
    QPushButton:focus {{
        border: 2px solid {accent};
    }}
    QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
        background-color: #050816;
        color: #f2f5ff;
        border: 1px solid {accent}55;
        border-radius: 8px;
        padding: 4px 6px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{
        border: 2px solid {accent};
    }}
    QTabWidget::pane {{
        border: 1px solid {accent}55;
        border-radius: 8px;
        background-color: #070a14;
    }}
    QTabBar::tab {{
        background-color: #0b1020;
        color: {accent};
        border: 1px solid {accent}44;
        border-radius: 6px;
        padding: 6px 10px;
        margin: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {accent};
        color: #050816;
    }}
    QLabel {{
        color: #f2f5ff;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QScrollBar:vertical {{
        background-color: #050816;
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background-color: {accent}66;
        border-radius: 5px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """


def classic_stylesheet(font_size: str) -> str:
    size = FONT_SIZES.get(font_size, 11)
    return f"""
    QWidget {{
        font-size: {size}px;
    }}
    QFrame[card="true"] {{
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 10px;
    }}
    QPushButton:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{
        border: 2px solid #2563eb;
    }}
    """


def apply_theme(app: QApplication, settings) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", FONT_SIZES.get(getattr(settings, "font_size", "medium"), 11)))
    if getattr(settings, "theme_mode", "classic") == "neon":
        app.setPalette(neon_palette(getattr(settings, "accent_color", "#ff00ff")))
        app.setStyleSheet(
            neon_stylesheet(
                getattr(settings, "accent_color", "#ff00ff"),
                getattr(settings, "glow_strength", "strong"),
                getattr(settings, "font_size", "medium"),
            )
        )
    else:
        app.setPalette(classic_palette())
        app.setStyleSheet(classic_stylesheet(getattr(settings, "font_size", "medium")))


def apply_glow(widget: QWidget, settings) -> None:
    if getattr(settings, "theme_mode", "classic") != "neon":
        widget.setGraphicsEffect(None)
        return
    color = normalize_accent(getattr(settings, "accent_color", "#ff00ff"))
    strength = getattr(settings, "glow_strength", "strong")
    radius = GLOW_RADII.get(strength, 28)
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(radius)
    effect.setColor(QColor(color))
    effect.setOffset(0, 0)
    widget.setGraphicsEffect(effect)


def clear_glow(widget: QWidget) -> None:
    widget.setGraphicsEffect(None)