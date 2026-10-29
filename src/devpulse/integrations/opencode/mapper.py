from typing import Any, Dict, List, Optional

from devpulse.domain.models import ContextMetrics, Model, Session, TokenUsage


def map_token_usage(data: Optional[Dict[str, Any]]) -> TokenUsage:
    if not data:
        return TokenUsage()
    cache = data.get("cache") or {}
    return TokenUsage(
        input=int(data.get("input", 0) or 0),
        output=int(data.get("output", 0) or 0),
        reasoning=int(data.get("reasoning", 0) or 0),
        cache_read=int(cache.get("read", 0) or 0),
        cache_write=int(cache.get("write", 0) or 0),
    )


def map_model(data: Optional[Dict[str, Any]]) -> Optional[Model]:
    if not data:
        return None
    limit = data.get("limit") or {}
    return Model(
        id=str(data.get("id", "")),
        provider_id=str(data.get("providerID", "")),
        name=str(data.get("name", data.get("id", ""))),
        context_limit=limit.get("context"),
        output_limit=limit.get("output"),
    )


def map_session(data: Dict[str, Any], model: Optional[Model] = None) -> Session:
    if not data:
        raise ValueError("Session data is required")
    time_data = data.get("time") or {}
    location = data.get("location") or {}
    return Session(
        id=str(data["id"]),
        project_id=str(data.get("projectID", "")),
        title=str(data.get("title", "")),
        directory=location.get("directory"),
        model=model,
        tokens=map_token_usage(data.get("tokens")),
        cost=float(data.get("cost", 0) or 0),
        updated_at=time_data.get("updated"),
    )


def calculate_context(messages: List[Dict[str, Any]], model: Optional[Model]) -> ContextMetrics:
    last_assistant = None
    for message in reversed(messages or []):
        if message.get("type") == "assistant" and message.get("tokens"):
            last_assistant = message
            break

    if not last_assistant:
        return ContextMetrics(source="unavailable")

    usage = map_token_usage(last_assistant.get("tokens"))
    used = usage.input + usage.cache_read
    limit = model.context_limit if model else None

    if limit:
        remaining = max(limit - used, 0)
        percentage = (used / limit) * 100 if limit else None
        return ContextMetrics(
            used_tokens=used,
            limit_tokens=limit,
            remaining_tokens=remaining,
            percentage=percentage,
            source="calculated",
        )

    return ContextMetrics(used_tokens=used, source="calculated")
