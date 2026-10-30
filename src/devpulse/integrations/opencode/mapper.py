from typing import Any, Dict, List, Optional

from devpulse.domain.models import ContextMetrics, Model, Session, TokenUsage
from devpulse.privacy import (
    sanitize_text,
    validate_model_payload,
    validate_session_payload,
    validate_token_payload,
)


def map_token_usage(data: Optional[Dict[str, Any]]) -> TokenUsage:
    if not data:
        return TokenUsage()
    validated = validate_token_payload(data)
    cache = validated.get("cache") or {}
    return TokenUsage(
        input=int(validated.get("input", 0) or 0),
        output=int(validated.get("output", 0) or 0),
        reasoning=int(validated.get("reasoning", 0) or 0),
        cache_read=int(cache.get("read", 0) or 0),
        cache_write=int(cache.get("write", 0) or 0),
    )


def map_model(data: Optional[Dict[str, Any]]) -> Optional[Model]:
    if not data:
        return None
    validated = validate_model_payload(data)
    if validated is None:
        return None
    limit = validated.get("limit") or {}
    return Model(
        id=sanitize_text(validated.get("id", ""), 128),
        provider_id=sanitize_text(validated.get("providerID", ""), 128),
        name=sanitize_text(validated.get("name", validated.get("id", "")), 128),
        context_limit=limit.get("context"),
        output_limit=limit.get("output"),
    )


def map_session(data: Dict[str, Any], model: Optional[Model] = None) -> Session:
    if not data:
        raise ValueError("Session data is required")
    validated = validate_session_payload(data)
    time_data = validated.get("time") or {}
    location = validated.get("location") or {}
    directory = location.get("directory")
    if directory is not None:
        directory = sanitize_text(directory, 512)
    return Session(
        id=sanitize_text(validated["id"], 128),
        project_id=sanitize_text(validated.get("projectID", ""), 128),
        title=sanitize_text(validated.get("title", ""), 256),
        directory=directory,
        model=model,
        tokens=map_token_usage(validated.get("tokens")),
        cost=float(validated.get("cost", 0) or 0),
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
