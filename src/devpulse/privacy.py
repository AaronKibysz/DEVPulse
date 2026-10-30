import base64
import hashlib
import os
import re
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken

from devpulse.domain.errors import ValidationError

_REGISTERED_SECRETS: set[str] = set()


def register_secret(secret: Optional[str]) -> None:
    if secret:
        _REGISTERED_SECRETS.add(secret)


def clear_registered_secrets() -> None:
    _REGISTERED_SECRETS.clear()


def validate_base_url(url: str) -> str:
    from urllib.parse import urlparse

    if not isinstance(url, str) or not url:
        raise ValidationError("OpenCode URL is required")
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValidationError("Only localhost connections are allowed")
    return url.rstrip("/")


def sanitize_text(value: Any, max_length: int = 256) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    text = text.replace("\x00", "")
    text = "".join(char for char in text if char.isprintable() or char in "\t\n\r")
    text = text.strip()
    return text[:max_length]


def sanitize_identifier(value: Any) -> str:
    return sanitize_text(value, 128)


def redact_sensitive_text(text: str, secrets: Optional[set[str]] = None) -> str:
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    secrets = secrets if secrets is not None else _REGISTERED_SECRETS
    result = text
    for secret in secrets:
        if secret:
            result = result.replace(secret, "[REDACTED]")
    result = re.sub(
        r"(?i)(password|token|authorization|secret)\s*[:=]\s*\S+",
        r"\1=[REDACTED]",
        result,
    )
    return result


class SecretRedactionFilter:
    def filter(self, record) -> bool:
        try:
            record.msg = redact_sensitive_text(str(record.msg), _REGISTERED_SECRETS)
            if record.args:
                record.args = tuple(
                    redact_sensitive_text(str(arg), _REGISTERED_SECRETS) if not isinstance(arg, (int, float, bool)) else arg
                    for arg in record.args
                )
        except Exception:
            return True
        return True


def _derive_key(pin: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(pin.encode("utf-8")))


def hash_pin(pin: str, salt: Optional[bytes] = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    digest = kdf.derive(pin.encode("utf-8"))
    return base64.b64encode(salt + digest).decode("ascii")


def verify_pin(pin: str, stored: Optional[str]) -> bool:
    if not stored:
        return False
    try:
        raw = base64.b64decode(stored.encode("ascii"))
    except (ValueError, TypeError):
        return False
    if len(raw) < 17:
        return False
    salt, digest = raw[:16], raw[16:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    try:
        kdf.verify(pin.encode("utf-8"), digest)
        return True
    except Exception:
        return False


def encrypt_data(data: bytes, pin: str) -> str:
    salt = os.urandom(16)
    key = _derive_key(pin, salt)
    token = Fernet(key).encrypt(data)
    return base64.b64encode(salt).decode("ascii") + ":" + token.decode("ascii")


def decrypt_data(token: str, pin: str) -> Optional[bytes]:
    if not isinstance(token, str) or ":" not in token:
        return None
    salt_b64, encrypted = token.split(":", 1)
    try:
        salt = base64.b64decode(salt_b64.encode("ascii"))
        key = _derive_key(pin, salt)
        return Fernet(key).decrypt(encrypted.encode("ascii"))
    except (InvalidToken, ValueError, TypeError):
        return None


def validate_token_payload(data: Any) -> dict:
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError("Token data must be an object")
    result = {}
    for key in ("input", "output", "reasoning"):
        value = data.get(key, 0)
        if value is None:
            value = 0
        if not isinstance(value, int) or isinstance(value, bool):
            try:
                value = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(f"Invalid token field: {key}") from exc
        result[key] = value
    cache = data.get("cache")
    if cache is None:
        cache = {}
    if not isinstance(cache, dict):
        raise ValidationError("Token cache data must be an object")
    for key in ("read", "write"):
        value = cache.get(key, 0)
        if value is None:
            value = 0
        if not isinstance(value, int) or isinstance(value, bool):
            try:
                value = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(f"Invalid cache field: {key}") from exc
        cache[key] = value
    result["cache"] = cache
    return result


def validate_model_payload(data: Any) -> Optional[dict]:
    if not data:
        return None
    if not isinstance(data, dict):
        raise ValidationError("Model data must be an object")
    model_id = data.get("id")
    if model_id is None or not isinstance(model_id, str):
        raise ValidationError("Model id is required")
    limit = data.get("limit")
    if limit is None:
        limit = {}
    if not isinstance(limit, dict):
        raise ValidationError("Model limit must be an object")
    context_limit = limit.get("context")
    output_limit = limit.get("output")
    for name, value in (("context", context_limit), ("output", output_limit)):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
            try:
                limit[name] = int(value)
            except (TypeError, ValueError) as exc:
                raise ValidationError(f"Invalid model limit: {name}") from exc
    return data


def validate_session_payload(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ValidationError("Session data must be an object")
    session_id = data.get("id")
    if not isinstance(session_id, str) or not session_id:
        raise ValidationError("Session id is required")
    if data.get("tokens") is not None:
        validate_token_payload(data.get("tokens"))
    if data.get("cost") is not None:
        try:
            float(data.get("cost"))
        except (TypeError, ValueError) as exc:
            raise ValidationError("Invalid session cost") from exc
    return data


def secure_file_permissions(path: str) -> None:
    try:
        if os.name == "posix":
            os.chmod(path, 0o600)
    except OSError:
        return


class RetryPolicy:
    def __init__(self, max_failures: int = 3) -> None:
        self.max_failures = max_failures
        self.failures = 0
        self.blocked = False

    def record_success(self) -> None:
        self.failures = 0
        self.blocked = False

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.max_failures:
            self.blocked = True

    def allow_retry(self) -> bool:
        return not self.blocked

    def reset(self) -> None:
        self.failures = 0
        self.blocked = False
