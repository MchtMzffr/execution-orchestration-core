"""Execution log/report redaction (INV-EXE-4: secret hygiene)."""

from typing import Any

# Common secret patterns (case-insensitive, normalized)
REDACT_PATTERNS = frozenset(
    {
        "password",
        "secret",
        "token",
        "key",
        "api_key",
        "auth",
        "credential",
        "private",
    }
)


def redact_execution_log(log_data: dict[str, Any]) -> dict[str, Any]:
    """
    Redact secret patterns from execution log data.
    
    Args:
        log_data: Execution log dict (input/output/context)
    
    Returns:
        Redacted dict with [REDACTED] markers
    """
    if not isinstance(log_data, dict):
        return log_data

    redacted: dict[str, Any] = {}
    for k, v in log_data.items():
        key_lower = k.lower().replace("-", "").replace("_", "")
        # Check if key matches any redact pattern
        should_redact = any(pattern in key_lower for pattern in REDACT_PATTERNS)

        if should_redact:
            redacted[k] = "[REDACTED]"
        elif isinstance(v, dict):
            redacted[k] = redact_execution_log(v)
        elif isinstance(v, list):
            redacted[k] = [
                redact_execution_log(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            redacted[k] = v

    return redacted
