from devpulse.privacy import (
    encrypt_data,
    decrypt_data,
    hash_pin,
    verify_pin,
    redact_sensitive_text,
    sanitize_text,
    validate_base_url,
    RetryPolicy,
    validate_token_payload,
)


def test_validate_base_url() -> None:
    assert validate_base_url("http://127.0.0.1:49374") == "http://127.0.0.1:49374"
    try:
        validate_base_url("http://example.com")
    except Exception:
        pass
    else:
        raise AssertionError("Expected validation error")


def test_sanitize_text() -> None:
    assert sanitize_text("  hello\x00world  ") == "helloworld"
    assert sanitize_text(None) == ""


def test_redact_sensitive_text() -> None:
    text = redact_sensitive_text("password=secret token=abc", {"secret"})
    assert "secret" not in text
    assert "[REDACTED]" in text


def test_pin_hash_and_verify() -> None:
    stored = hash_pin("1234")
    assert verify_pin("1234", stored)
    assert not verify_pin("0000", stored)


def test_encrypt_decrypt() -> None:
    token = encrypt_data(b"hello", "1234")
    assert decrypt_data(token, "1234") == b"hello"
    assert decrypt_data(token, "0000") is None


def test_retry_policy() -> None:
    policy = RetryPolicy(max_failures=2)
    policy.record_failure()
    assert policy.allow_retry()
    policy.record_failure()
    assert not policy.allow_retry()
    policy.reset()
    assert policy.allow_retry()


def test_validate_token_payload() -> None:
    data = validate_token_payload({"input": "10", "output": 5, "cache": {"read": "2", "write": 1}})
    assert data["input"] == 10
    assert data["cache"]["read"] == 2
