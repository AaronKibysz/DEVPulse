import time
from typing import List, Optional, Tuple

from devpulse.domain.models import MetricSample, Session


def sample_from_session(session: Session, timestamp: float | None = None) -> MetricSample:
    metrics = session.context_metrics
    return MetricSample(
        session_id=session.id,
        timestamp=time.time() if timestamp is None else timestamp,
        input_tokens=session.tokens.input,
        output_tokens=session.tokens.output,
        cache_read_tokens=session.tokens.cache_read,
        context_used=metrics.used_tokens if metrics is not None else None,
        context_limit=metrics.limit_tokens if metrics is not None else None,
        context_percentage=metrics.percentage if metrics is not None else None,
        cost=session.cost,
    )


def token_bar_values(session: Session) -> Tuple[List[str], List[int]]:
    return (
        ["Input", "Output", "Cache"],
        [session.tokens.input, session.tokens.output, session.tokens.cache_read],
    )


def context_values(session: Session) -> Tuple[Optional[int], Optional[int], Optional[float]]:
    metrics = session.context_metrics
    if metrics is None or metrics.source == "unavailable" or metrics.used_tokens is None:
        return None, None, None
    return metrics.used_tokens, metrics.limit_tokens, metrics.percentage


def context_trend_points(samples: List[MetricSample]) -> List[Tuple[float, float]]:
    return [
        (sample.timestamp, sample.context_percentage)
        for sample in samples
        if sample.context_percentage is not None
    ]