from devpulse.integrations.opencode.mapper import (
    calculate_context,
    map_model,
    map_session,
    map_token_usage,
)


def test_map_token_usage() -> None:
    data = {"input": 10, "output": 5, "reasoning": 2, "cache": {"read": 3, "write": 1}}
    usage = map_token_usage(data)
    assert usage.input == 10
    assert usage.output == 5
    assert usage.reasoning == 2
    assert usage.cache_read == 3
    assert usage.cache_write == 1


def test_map_model() -> None:
    data = {"id": "m1", "providerID": "p1", "name": "Model One", "limit": {"context": 1000, "output": 500}}
    model = map_model(data)
    assert model is not None
    assert model.id == "m1"
    assert model.context_limit == 1000


def test_map_session() -> None:
    data = {
        "id": "ses_1",
        "projectID": "proj_1",
        "title": "Test",
        "location": {"directory": "/tmp"},
        "tokens": {"input": 1, "output": 2, "reasoning": 0, "cache": {"read": 0, "write": 0}},
        "cost": 0,
        "time": {"updated": 123},
    }
    session = map_session(data)
    assert session.id == "ses_1"
    assert session.directory == "/tmp"


def test_calculate_context() -> None:
    model_data = {"id": "m1", "providerID": "p1", "name": "Model", "limit": {"context": 100, "output": 50}}
    model = map_model(model_data)
    messages = [
        {"type": "assistant", "tokens": {"input": 10, "output": 2, "reasoning": 0, "cache": {"read": 5, "write": 0}}}
    ]
    metrics = calculate_context(messages, model)
    assert metrics.used_tokens == 15
    assert metrics.limit_tokens == 100
    assert metrics.remaining_tokens == 85
    assert metrics.source == "calculated"


def test_calculate_context_unavailable_without_assistant() -> None:
    metrics = calculate_context([], None)
    assert metrics.source == "unavailable"
    assert metrics.used_tokens is None


def test_calculate_context_without_limit() -> None:
    model = map_model({"id": "m1", "providerID": "p1", "name": "Model"})
    messages = [{"type": "assistant", "tokens": {"input": 5, "output": 1, "reasoning": 0, "cache": {"read": 2, "write": 0}}}]
    metrics = calculate_context(messages, model)
    assert metrics.used_tokens == 7
    assert metrics.limit_tokens is None
    assert metrics.percentage is None
    assert metrics.source == "calculated"
