from types import SimpleNamespace

from devpulse.ui.theme import chart_colors, normalize_accent, secondary_accent


def test_chart_colors_neon() -> None:
    settings = SimpleNamespace(theme_mode="neon", accent_color="#ff00ff")
    colors = chart_colors(settings)
    assert colors["background"] == "#101522"
    assert "used" in colors


def test_chart_colors_classic() -> None:
    settings = SimpleNamespace(theme_mode="classic", accent_color="#2563eb")
    colors = chart_colors(settings)
    assert colors["background"] == "#f8fafc"


def test_normalize_accent() -> None:
    assert normalize_accent("#abc") == "#aabbcc"
    assert normalize_accent("magenta") == "#ff00ff"


def test_secondary_accent() -> None:
    assert secondary_accent("#ff00ff") == "#00f5ff"