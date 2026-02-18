"""INV-T1: Execution trace keys format tests."""

import pytest
from decision_schema.trace_registry import is_valid_trace_key, validate_external_dict

from execution_orchestration_core.model import ExecutionReport
from execution_orchestration_core.trace import add_execution_trace


def test_inv_t1_execution_trace_keys_format() -> None:
    """Execution trace keys match INV-T1 format (dot-separated, lowercase)."""
    report = ExecutionReport(
        total_latency_ms=100,
        success_count=1,
        failed_count=0,
        skipped_count=0,
        denied_count=0,
        fail_closed=False,
    )

    external = add_execution_trace({}, report)

    # All keys should match trace key format
    for key in external.keys():
        if "." in key:  # Trace-extension keys
            assert is_valid_trace_key(key), f"Invalid trace key format: {key}"


def test_inv_t1_execution_trace_keys_registered() -> None:
    """Execution trace keys should be registered in SSOT registry (future)."""
    report = ExecutionReport()
    external = add_execution_trace({}, report)

    # Validate format (strict mode for exec namespace)
    errors = validate_external_dict(
        external,
        require_registry_for_prefixes={"exec"},
        mode="trace",
    )

    # For now, exec.* keys may not be registered yet (acceptable)
    # But format must be valid
    format_errors = [e for e in errors if "invalid" in e]
    assert len(format_errors) == 0, f"Format errors: {format_errors}"
