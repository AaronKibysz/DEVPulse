from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class MetricSample:
    session_id: str
    timestamp: float
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    context_used: Optional[int] = None
    context_limit: Optional[int] = None
    context_percentage: Optional[float] = None
    cost: float = 0.0


@dataclass
class TokenUsage:
    input: int = 0
    output: int = 0
    reasoning: int = 0
    cache_read: int = 0
    cache_write: int = 0


@dataclass
class Model:
    id: str
    provider_id: str
    name: str
    context_limit: Optional[int] = None
    output_limit: Optional[int] = None


@dataclass
class Session:
    id: str
    project_id: str
    title: str
    directory: Optional[str] = None
    model: Optional[Model] = None
    tokens: TokenUsage = field(default_factory=TokenUsage)
    cost: float = 0.0
    active: bool = False
    updated_at: Optional[int] = None
    context_metrics: Optional[ContextMetrics] = None


@dataclass
class Instance:
    id: str
    base_url: str
    version: Optional[str] = None


@dataclass
class ContextMetrics:
    used_tokens: Optional[int] = None
    limit_tokens: Optional[int] = None
    remaining_tokens: Optional[int] = None
    percentage: Optional[float] = None
    source: str = "unavailable"
