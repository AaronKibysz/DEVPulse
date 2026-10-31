from collections import defaultdict, deque
from typing import Deque, Dict, List

from devpulse.domain.models import MetricSample

MAX_SAMPLES_PER_SESSION = 50


class MetricHistory:
    def __init__(self, max_samples: int = MAX_SAMPLES_PER_SESSION) -> None:
        self.max_samples = max_samples
        self._samples: Dict[str, Deque[MetricSample]] = defaultdict(lambda: deque(maxlen=max_samples))

    def add(self, sample: MetricSample) -> None:
        self._samples[sample.session_id].append(sample)

    def samples(self, session_id: str) -> List[MetricSample]:
        return list(self._samples.get(session_id, ()))

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self._samples.clear()
        else:
            self._samples.pop(session_id, None)

    def latest(self, session_id: str) -> MetricSample | None:
        items = self._samples.get(session_id)
        if not items:
            return None
        return items[-1]