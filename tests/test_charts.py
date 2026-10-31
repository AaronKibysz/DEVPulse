from devpulse.domain.models import ContextMetrics, Session, TokenUsage
from devpulse.ui.charts import context_trend_points, context_values, token_bar_values


def test_token_bar_values() -> None:
    session = Session(id="s1", project_id="p1", title="Test", tokens=TokenUsage(input=1, output=2, cache_read=3))
    categories, values = token_bar_values(session)
    assert categories == ["Input", "Output", "Cache"]
    assert values == [1, 2, 3]


def test_context_values_unavailable() -> None:
    session = Session(id="s1", project_id="p1", title="Test")
    assert context_values(session) == (None, None, None)


def test_context_values_available() -> None:
    session = Session(id="s1", project_id="p1", title="Test", context_metrics=ContextMetrics(used_tokens=10, limit_tokens=20, percentage=50.0, source="calculated"))
    assert context_values(session) == (10, 20, 50.0)


def test_context_trend_points_filters_none() -> None:
    from devpulse.domain.models import MetricSample

    samples = [
        MetricSample(session_id="s1", timestamp=1.0, context_percentage=10.0),
        MetricSample(session_id="s1", timestamp=2.0, context_percentage=None),
        MetricSample(session_id="s1", timestamp=3.0, context_percentage=30.0),
    ]
    assert context_trend_points(samples) == [(1.0, 10.0), (3.0, 30.0)]