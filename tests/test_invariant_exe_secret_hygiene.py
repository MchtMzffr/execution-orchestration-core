# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""INV-EXE-5: Secret/log hygiene tests."""

import pytest
from execution_orchestration_core.redaction import redact_execution_log


def test_inv_exe_5_secret_patterns_redacted() -> None:
    """Secret patterns in execution logs are redacted."""
    log_data = {
        "action": "ACT",
        "api_key": "secret-key-123",
        "password": "mypassword",
        "token": "bearer-token",
        "normal_field": "value",
    }

    redacted = redact_execution_log(log_data)

    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["token"] == "[REDACTED]"
    assert redacted["normal_field"] == "value"  # Not redacted


def test_inv_exe_5_nested_secrets_redacted() -> None:
    """Nested secret patterns are redacted."""
    log_data = {
        "context": {
            "auth": {"api_key": "secret", "username": "user"},
            "normal": {"value": "data"},
        },
    }

    redacted = redact_execution_log(log_data)

    assert redacted["context"]["auth"]["api_key"] == "[REDACTED]"
    assert redacted["context"]["auth"]["username"] == "user"  # Not a secret pattern
    assert redacted["context"]["normal"]["value"] == "data"


def test_inv_exe_5_case_insensitive_redaction() -> None:
    """Redaction is case-insensitive."""
    log_data = {
        "API_KEY": "secret",
        "Password": "secret",
        "SECRET_TOKEN": "secret",
    }

    redacted = redact_execution_log(log_data)

    assert redacted["API_KEY"] == "[REDACTED]"
    assert redacted["Password"] == "[REDACTED]"
    assert redacted["SECRET_TOKEN"] == "[REDACTED]"
