# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
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

        # Process nested structures first (recursive)
        if isinstance(v, dict):
            processed_value = redact_execution_log(v)
            # Keep the structure even if key matches pattern (nested keys are processed)
            redacted[k] = processed_value
        elif isinstance(v, list):
            redacted[k] = [
                redact_execution_log(item) if isinstance(item, dict) else item for item in v
            ]
        elif should_redact:
            # Redact non-dict values if key matches pattern
            redacted[k] = "[REDACTED]"
        else:
            redacted[k] = v

    return redacted
