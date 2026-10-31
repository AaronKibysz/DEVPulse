from devpulse.application.metric_history import MetricHistory
from devpulse.domain.models import MetricSample


def test_metric_history_limits_samples() -> None:
    history = MetricHistory(max_samples=2)
    for value in (10.0, 20.0, 30.0):
        history.add(MetricSample(session_id="s1", timestamp=value, context_percentage=value))
    samples = history.samples("s1")
    assert [sample.timestamp for sample in samples] == [20.0, 30.0]


def test_metric_history_clear_session() -> None:
    history = MetricHistory()
    history.add(MetricSample(session_id="s1", timestamp=1.0))
    history.add(MetricSample(session_id="s2", timestamp=2.0))
    history.clear("s1")
    assert history.samples("s1") == []
    assert len(history.samples("s2")) == 1