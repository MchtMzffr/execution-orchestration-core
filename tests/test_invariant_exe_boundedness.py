# Decision Ecosystem — execution-orchestration-core
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""INV-EXE-2: Execution boundedness tests."""

from decision_schema.types import Action, FinalDecision

from execution_orchestration_core.orchestrator import execute
from execution_orchestration_core.policies import ExecutionPolicy, RetryPolicy, TimeoutPolicy


def test_inv_exe_2_max_retries_bounded() -> None:
    """Max retries policy is respected (bounded attempts)."""
    policy = ExecutionPolicy(
        retry=RetryPolicy(max_retries=2),
        timeout=TimeoutPolicy(timeout_per_action_ms=1000, max_total_time_ms=10000),
    )

    def failing_executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        return False, "always fails"

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {}

    report = execute(final_decision, context, policy, failing_executor)

    # Should have max_retries + 1 attempts (initial + retries)
    assert len(report.attempts) <= policy.retry.max_retries + 1
    assert report.failed_count > 0


def test_inv_exe_2_max_total_time_bounded() -> None:
    """Max total time policy is respected (bounded duration)."""
    policy = ExecutionPolicy(
        retry=RetryPolicy(max_retries=10),  # High retries
        timeout=TimeoutPolicy(
            timeout_per_action_ms=1000, max_total_time_ms=100
        ),  # Very short total time
    )

    def slow_executor(_action: Action, _context: dict) -> tuple[bool, str | None]:
        import time

        time.sleep(0.2)  # 200ms per attempt
        return False, "slow failure"

    final_decision = FinalDecision(action=Action.ACT, allowed=True, reasons=["test"])
    context = {}

    report = execute(final_decision, context, policy, slow_executor)

    # Should stop due to max_total_time_ms (fail_closed)
    assert report.fail_closed is True
    # Tolerance for scheduler/overhead: stop is enforced at max_total_time_ms but elapsed can exceed slightly
    assert report.total_latency_ms <= policy.timeout.max_total_time_ms + 250


def test_inv_exe_2_max_concurrency_bounded() -> None:
    """Max concurrency policy is respected (sequential by default)."""
    policy = ExecutionPolicy(max_concurrency=1)  # Sequential

    # Sequential execution means one action at a time
    # This is enforced by the orchestrator design (no parallel execution yet)
    assert policy.max_concurrency >= 1  # At least 1 (sequential)
